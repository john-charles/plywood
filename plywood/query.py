from urlparse import parse_qsl

class Query(dict):
    
    def __init__(self, query_string):
        
        query_dict = dict()
        
        for key, val in parse_qsl(query_string):
            if key in query_dict:
                if isinstance(query_dict[key], list):
                    query_dict[key].append(val)
                else:
                    query_dict[key] = list(query_dict[key], val)
            else:
                query_dict[key] = val
            
        dict.__init__(self, query_dict)
        
        
    
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
