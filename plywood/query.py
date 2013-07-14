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
import tempfile, string, json

from kinds import *
from collections import deque
from urlparse import parse_qsl
from exceptions import Server413Exception

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def parse_headers(head):
    """Parses headers into list((header-name, header-value, header-options))"""
    
    def proc_val(val, opts):
        val = val.strip()
        if '=' in val:
            key, val = val.split('=')
            opts[key] = val[1:-1]
        else:
            opts[val] = None

    if head.endswith("\r\n\r\n"):
        head = head[:-2]

    headers = []
    
    for line in head.split('\r\n'):

        opts = {}
        name, vals = line.split(':', 1)

        # Not all headers have options, so we
        # need to handle that here!
        vals = vals.split(';',1)
        if len(vals) == 1:
            value = vals[0]
            vals = ""
        else:
            value, vals = vals
        
        [proc_val(v, opts) for v in vals.split(';')]
        
        headers.append((name, value.strip(), opts))

    return headers

def parse_multipart(reader, boundary, part_callback):

    # NOTE: I have not read anywhere that this is needed,
    # but it is, I've also noticed other implementations
    # doing it!
    boundary = "--" + boundary
    sum_boundary = sum([ord(c) for c in boundary])
    
    buff = reader(len(boundary))
    
    sum_rolling = sum([ord(c) for c in buff])
    
    curr_head_flag = True
    curr_head = ""
    curr_body = tempfile.NamedTemporaryFile()

    while True:

        last_chr = buff[:1]
        next_chr = reader(1)
        if next_chr == '': break
        else:
            # If we are parsing the header.
            if curr_head_flag:
                # Append the next character to the header.
                curr_head += next_chr
                
                # The check to see if we've reached the end
                # of the header, delimited by '\n\n'
                if curr_head.endswith("\r\n\r\n"):
                    # if we have, set our header flag
                    # to false
                    curr_head_flag = False
            else:
                # Otherwise, were not parsing the header
                # so append the char to the body!
                curr_body.write(next_chr)
        
        buff = buff[1:]
        buff = buff + next_chr

        sum_rolling -= ord(last_chr)
        sum_rolling += ord(next_chr)

        if sum_rolling == sum_boundary:
            if buff == boundary:                
                # Process the current chunk!
                curr_body.truncate(curr_body.tell() - len(boundary))
                curr_body.seek(0)
                part_callback(curr_head.strip(), curr_body)

                # Initialize env for next part.
                curr_head_flag = True
                curr_head = ""
                curr_body = tempfile.NamedTemporaryFile()

    # Note: According to the RFC's we should never get here
    # with straggling data. Also, at this point our part_head
    # data should contain only '--' If so we need to clean up
    # by closing the file. However, if the head does not equal
    # '--' we need to throw some kind of error because a proper
    # multipart message, must end in '--'.
    curr_body.close()
    
    if curr_head.strip() != "--":
        raise ValueError("Pre-mature end of input while parsing multipart")


def query_dict_from_multipart(reader, boundary):

    results = {}  

    def callback(head, body):
        
        headers = parse_headers(head)

        for header, val, opts in headers:
            if header == "Content-Disposition":
                if val != "form-data":
                    raise ValueError("Content-Disposition must be form-data")
                
                name = opts.pop('name').replace('"','')
                if 'filename' in opts:                    
                    results[name] = (body, opts)
                else:                    
                    results[name] = body.read().strip()
                    body.close()
        
            
    parse_multipart(reader, boundary, callback)
    
    return results


class Query(dict):
    
    def __init__(self, input_source, content_type=None, content_length=0):
        
        if isinstance(input_source, str):
            self.__init_urlencoded(input_source)
        elif content_type == "application/x-www-form-urlencoded":
            self.__init_urlencoded(input_source, content_length)
        elif content_type.startswith("multipart/form-data"):
            self.__init_multipart(input_source, content_type, content_length)
        elif content_type.startswith("application/json"):
            self.__init__json(input_source, content_type, content_length)
        
        
    def __init_urlencoded(self, reader, length=None):
        """This process data as urlencoded"""
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
        
    def __get_boundry(self, content_type):
        
        type_dict = dict()
        for part in content_type.split(';')[1:]:
            key, value = part.split('=')
            type_dict[key.strip().lower()] = value.strip()
        
        return type_dict['boundary']
    
        
    def __init_multipart(self, reader, ctype, length):
        """Parse and init based on multipart/form-data"""
        boundary = self.__get_boundry(ctype)        
        dict.__init__(self, query_dict_from_multipart(reader, boundary))
        
        
    def __init__json(self, reader, c_type, length):        
        json_data = reader(length)
        self.update(json.loads(json_data))
    
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
