import tempfile
from StringIO import StringIO
from urlparse import parse_qsl
from exceptions import Server413Exception

class Query(dict):
    
    def __init__(self, post_data_reader, content_type, content_length):
        
        if content_type == "application/x-www-form-urlencoded":
            self.__init_urlencoded(post_data_reader, content_length)
        elif content_type.startswith("multipart/form-data"):
            self.__init_multipart(post_data_reader, content_type, content_length)        
        
    def __init_urlencoded(self, reader, length):
        
        if length > 1024:
            raise Server413Exception("The request was too big","")
        
        query_dict = dict()
        
        for key, val in parse_qsl(reader()):
            if key in query_dict:
                if isinstance(query_dict[key], list):
                    query_dict[key].append(val)
                else:
                    query_dict[key] = list((query_dict[key], val))
            else:
                query_dict[key] = val
            
        dict.__init__(self, query_dict)
        
    def __init_multipart(self, reader, ctype, length):        
        boundary = self.__get_boundry(ctype)
        local_file = self.__copy_to_temp(reader, length)
                
        dict.__init__(self, self.__iter_parts(local_file, boundary))
        
    def __get_part(self, local_file, boundary):
        
        part_meta = list()
        meta_line = local_file.readline()
        while meta_line != '\r\n':
            part_meta.append(meta_line)
            meta_line = local_file.readline()
            
        print part_meta
        
        
        
        
        
    def __iter_parts(self, local_file, boundary):
        
        first_line = local_file.readline()
        if not first_line.startswith(boundary):
            raise Exception("File did not startwith delimiter.")
        
        while True:
            yield self.__get_part(local_file, boundary)
        
        
    def __get_boundry(self, content_type):
        
        type_dict = dict()
        for part in content_type.split(';')[1:]:
            key, value = part.split('=')
            type_dict[key] = value
            
        return type_dict['boundary']
    
    def __copy_to_temp(self, reader, length):
        
        if length < 1024:
            local_file = StringIO(reader())
        else:
            local_file = tempfile.TemporaryFile()
            
        while True:
            buff = local_file(1024)
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
