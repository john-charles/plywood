#!/usr/bin/env python
__all__ = ['MemorySession', 'CookieSession']
"""
Since plywood doesn't know about databases, it just
    work on the http protocal level. We will create
    2 default sessions wrappers.

    MemorySession a session wrapper that stores
        all session data in the servers memory. This
        wrapper is most likely not the best for production
        but might be useful for development.
        
    CookieSession a session wrapper that stores
        session data in cookies. This is more useful
        in production and is secured by encrypting and
        signing all the session data.
        
"""
from wrappers import Wrapper

class Session:
    
    __session_id = None
    
    def __init__(self):
        raise NotImplemented()
    
    def clear(self):
        raise NotImplemented()
    
    def get(self, name, default=None):
        raise NotImplemented()
    
    @property
    def id(self, value=None):
        if value:
            self.__session_id = value
        else:
            return self.__session_id
            
    
    def __contains__(self, name):
        raise NotImplemented()
    
    def __getitem__(self, name):
        raise NotImplemented()
    
    def __setitem__(self, name, value):
        raise NotImplemented()
    
    def __delete__(self, name):
        raise NotImplemented()


class MemorySession(Session):
    
    def __init__(self, session_dict):
        self.session_dict = session_dict
        
    def clear(self):
        self.session_dict.clear()
        
    def get(self, name, default=None):
        return self.session_dict.get(name, default)
    
    def __contains__(self, name):
        return name in self.session_dict
    
    def __getitem__(self, name):
        return self.session_dict[name]
    
    def __setitem__(self, name, value):
        self.session_dict[name] = value
        
    def __delete__(self, name):
        del self.session_dict[name]
        
    
    
    
    
    
    
    

