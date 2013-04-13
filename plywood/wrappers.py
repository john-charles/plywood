__all__ = ['WList', 'wconfig', 'Wrapper', 'CookieSessionWrapper', 'MemorySessionWrapper']

from uuid import uuid4
from imputil import import_entity
from session import CookieSession, MemorySession

class Wrapper:
    
    def __init__(self, options):
        pass
    
    def request(self, request):
        pass
    
    def response(self, response):
        pass 
    
class WList:
    
    default_options = {}
    wrapper_list = list()
    
    def __init__(self, *args):
        if len(args) > 0 and isinstance(args[0], dict):
            default_options = args[0]
            self.wrapper_list = args[1:]
        else:
            self.wrapper_list = args
            
    def __iter__(self):        
        return self.wrapper_list.__iter__()
    
    def __repr__(self):
        return "<WList%s>" % repr(self.wrapper_list)
            
        
    
    
# Configure a wrapper.
#   If the wrapper is a name, the class is imported
#   and instantiated given the options dictionary.
#   
def wconfig(class_name, options={}):    
    return (class_name, options)


class CookieSessionWrapper(Wrapper):
    
    def __init__(self, options):
        self.options = options
        
    
    def request(self, request):
        
        if 'session_id' in request.cookies:
            session_id = request.cookies['session_id']
            request.session = CookieSession(session_id, request.cookies, self.options)
        else:
            session_id = uuid4().hex
            request.session = CookieSession(session_id, request.cookies, self.options)
            request.session.on_start()
        
    def response(self, response):
        
        response.set_cookie("session_id", response.request.session.id)
        for morsel in response.request.session.to_cookies():
            response.cookies += morsel



class MemorySessionWrapper(Wrapper):
    
    def __init__(self, options):
        self.options = options
        self.sessions = dict()
        print """Warning:
    MemorySession's are designed for development. Use either
    CookieSessionWrapper, or a third party SessionWrapper for
    production systems."""
        
    def request(self, request):
        
        if 'session_id' in request.cookies:
            session_id = request.cookies['session_id']
            request.session = MemorySession(
                self.sessions.get(session_id, dict()))
        else:
            session_id = uuid4().hex
            request.session = MemorySession(dict())
            request.session.on_start()
        
        request.session.id = session_id
            
    def response(self, response):
        
        request = response.request
        self.sessions[request.session.id] = request.session.session_dict 
        response.set_cookie("session_id", response.request.session.id, path="/")
            
        
    
    
    
    
    