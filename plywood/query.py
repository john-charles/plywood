"""
This file is part of plywood.
    
    Copyright 2013 John-Charles D. Sokolow - <john.charles.sokolow@gmail.com>

    plywood is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    plywood is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with plywood.  If not, see <http://www.gnu.org/licenses/>.
    
Please see README for usage details.   
"""
__all__ = ['Query']
import tempfile, string

from kinds import *
from collections import deque
from urlparse import parse_qsl
from exceptions import Server413Exception

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# TODO: Ideas to make this more efficient, use
#   a running checksum. Each byte popped is subtracted
#   from the sum each byte add is also added to the sum
#   before starting sum the search delimiter. If the
#   delimiter sum == the current sum, then we have a
#   candidate. Do a string.join and a compare.
#   this should greatly reduce the number of string
#   joins and comparisons.
def stream_search(filelike, delimiter, max_read=-1):
    
    slices = list()
    current_slice = list((None, None))
    max_read_set = False if max_read == -1 else True
    buffer_size = read_count = len(delimiter)    
    data_buffer = deque(filelike.read(buffer_size), buffer_size)
    
    if string.join(data_buffer, '') == delimiter:
        current_slice[0] = buffer_size
    else:
        current_slice[0] = 0
        
    if not max_read_set: max_read = buffer_size * 2
        
    while read_count <= max_read:
        
        byte = filelike.read(1)
        if not byte: break
        data_buffer.append(byte)
        read_count += 1
        
        if string.join(data_buffer, '') == delimiter:
            current_slice[1] = read_count - buffer_size
            slices.append(current_slice)
            current_slice = list((read_count, None))
            
        if not max_read_set:
            max_read += 1
            
    return slices


class Query(dict):
    
    def __init__(self, input_source, content_type=None, content_length=0):
        
        if isinstance(input_source, str):
            self.__init_urlencoded(input_source)
        elif content_type == "application/x-www-form-urlencoded":
            self.__init_urlencoded(input_source, content_length)
        elif content_type.startswith("multipart/form-data"):
            self.__init_multipart(input_source, content_type, content_length)
        
        
    def __init_urlencoded(self, reader, length=None):
        
        if length > 1024:
            raise Server413Exception("The request was too big","")
        
        query_dict = dict()
        query_string = reader(length) if length else reader
        
        for key, val in parse_qsl(query_string):
            if key in query_dict:
                if isinstance(query_dict[key], list):
                    query_dict[key].append(val)
                else:
                    query_dict[key] = list((query_dict[key], val))
            else:
                query_dict[key] = val
            
        dict.__init__(self, query_dict)
        
    def __matalines_to_dict(self, meta_lines):
        
        meta_dict = dict()
        for line in meta_lines:
            key, value = line.split(':')
            
            if not value.count(';'):
                value = (value.strip(), {})
            else:
                attrs = value.strip().split(';')
                
                value = attrs[0]
                attrs = attrs[1:]
                
                attr_dict = dict()
                
                for attr in attrs:
                    akey, avalue = attr.split('=')
                    attr_dict[akey.strip()] = avalue.strip().replace('"','')
                    
                value = (value, attr_dict)
                
            meta_dict[key.strip()] = value
            
        return meta_dict
    
    def __copy_slice(self, src, dst, start, end):
        
        dst.seek(0)
        src.seek(start)
        
        while start < end:
            # This get's the smaller of the rest of
            # the size left to be read or the block
            # size. So that it will read block size
            # until the remainder is smaller.
            chunk_size = min(end - start, 4096)
            start += chunk_size
            chunk = src.read(chunk_size)
            dst.write(chunk)
            
        dst.seek(0)
        
    def __parse_slice(self, local_file, slice_info):
        
        meta_lines = list()
        meta_length = 0
        # We know that the slice will actually have
        # two characters, \r\n on it. hence + 2
        slice_start = slice_info[0] + 2
        local_file.seek(slice_start)
        
        current_line = local_file.readline()
        meta_length += len(current_line)
        
        while current_line != '\r\n':
            meta_lines.append(current_line)
            current_line = local_file.readline()
            meta_length += len(current_line)
            if not current_line: break
        
        meta_end = slice_start + meta_length
        if meta_end > slice_info[1]:
            raise Exception("Bad data")
        
        # This should be the beginning of the data.
        # it is the slices end - (slice beginning + metan length)
        data_length = slice_info[1] - meta_end        
        
        # Process the actual data.
        meta_dict = self.__matalines_to_dict(meta_lines)
        
        cdisp, cattrs = meta_dict['Content-Disposition']
        if 'Content-Type' in meta_dict or 'filename' in cattrs:
            # It appears that we have a file here!
            if data_length > 1024:
                content_file = tempfile.TemporaryFile()
            else:
                content_file = StringIO()
                
            ## Give the caller a way to get the meta information
            ## about this file.
            #content_file.meta_dict = meta_dict
            
            self.__copy_slice(local_file, content_file,
                              meta_end, slice_info[1])
            
            return cattrs['name'], content_file
        
        else:
            data_content = local_file.read(data_length)
            # Valid data her will never have a '\r\n' in it
            # so get rid of it.
            cr_at = data_content.find('\r\n')
            if cr_at > -1:
                data_content = data_content[:cr_at]
            
            return cattrs['name'], data_content
        
    def __init_multipart(self, reader, ctype, length):
                
        boundary = self.__get_boundry(ctype)        
        
        local_file = self.__copy_to_temp(reader, length)        
        slices = stream_search(local_file, boundary)
        
        query_dict = dict()
        for slice_info in slices:
            try:
                name, value = self.__parse_slice(local_file, slice_info)
                
                if name in query_dict:
                    value = query_dict[name]
                    if isinstance(value, list):
                        query_dict[name].append(value)
                    else:
                        query_dict[name] = list(query_dict[name], value)
                else:
                    query_dict[name] = value
            except Exception, e:
                pass
        
        # Let's not leave tons of tempfiles laying around.
        local_file.close()
        
        dict.__init__(self, query_dict)
        
    def __get_boundry(self, content_type):
        
        type_dict = dict()
        for part in content_type.split(';')[1:]:
            key, value = part.split('=')
            type_dict[key.strip().lower()] = value.strip()
        
        return type_dict['boundary']
    
    def __copy_to_temp(self, reader, length):
        
        if length < 1024:
            local_file = StringIO(reader())
        else:
            local_file = tempfile.TemporaryFile()
            
        read_count = 0
            
        while True:
            next_read = length - read_count
            buff = reader(min(next_read, 4096))
            local_file.write(buff)
            if not buff: break
            
        local_file.seek(0)
        return local_file
    
    def get(self, name, default=None, inset=None, istype=None, inrange=None, shorter_than=None, plaintext=False):
        
        value = dict.get(self, name, default)
        
        if inset:
            if value not in inset:
                if default:
                    value = default
                else:
                    raise ValueError("Value %s not in set(%s)!" % (value, inset))
                
        if istype:
            try:
                value = istype(value)
            except TypeError, e:
                if default:
                    value = default
                else:
                    raise ValueError("Convesion to type raise TypeError(%s)" % e.message)
                
        if inrange:
            lower, upper = inrange
            if value not in range(lower, upper):
                if default: value = default
                else: raise ValueError("Value %s is not within range(%s, %s)" % (
                    value, lower, upper))
                
        if shorter_than:
            if len(value) > shorter_than:
                if default: value = default
                else: raise ValueError("Value '%s' is not shorter_than %s" % (
                    value[:7] + "...", shorter_than))
                    
        return value

    def __repr__(self):
        return "<Query%s>" % dict.__repr__(self)
    
    def __del__(self):
        
        for item in self.itervalues():
            if isinstance(item, file):
                try:
                    file.close()
                except:
                    pass
