__all__ = ['WList', 'wconfig', 'Wrapper', 'MemorySessionWrapper']

from uuid import uuid4
from imputil import import_entity
from session import MemorySession

class Wrapper:
    
    def __init__(self, options):
        raise NotImplemented()
    
    def request(self, request):
        raise NotImplemented()
    
    def response(self, response):
        raise NotImplemented()
    
class WList:
    
    default_options = {}
    wrapper_list = list()
    
    def __init__(self, *args):    
        if len(args) > 0 and isinstance(args[0], dict):
            default_options = args[0]
            wrapper_list = args[1:]
        else:
            wrapper_list = args
            
    def __iter__(self):        
        return self.wrapper_list.__iter__()
            
        
    
    
# Configure a wrapper.
#   If the wrapper is a name, the class is imported
#   and instantiated given the options dictionary.
#   
def wconfig(class_name, options={}):    
    return (wrapper, options)



class MemorySessionWrapper(Wrapper):
    
    def __init__(self, options):
        self.options = options
        self.sessions = dict()
        
    def request(self, request):
        
        if 'session_id' in request.cookies:
            session_id = request.cookies['session_id']
            session_data = self.sessions[session_id]
            request.session = MemorySession(session_data)
        else:
            session_id = uuid4().hex
            request.session = MemorySession(dict())
            
        request.session.id = session_id
            
    def response(self, response):        
        response.SetCookie("session_id", response.request.session.id)
            
        
    
    
    
    
    