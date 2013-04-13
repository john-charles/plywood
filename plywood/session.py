#!/usr/bin/env python
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

USAGE:
Since plywood doesn't know about databases, it just
    work on the http protocal level. We will create
    2 default sessions wrappers.

    MemorySession a session wrapper that stores
        all session data in the servers memory. This
        wrapper is most likely not the best for production
        but might be useful for development.
        
    CookieSession a session wrapper that stores session
        data in cookies. More useful in a production
        environment CookieSession stores all pickleable 
        python objects as base64 encoded text. However,
        before sending the pickled data to the client
        it hashes that data, the session_id and the servers
        secret key to create a signature. It then prepends
        that signature to the cookie data. When the cookie
        is retrieved from the client this process repeated
        and the two signatures are compared. If the cookie
        has been tampered with the signatures will fail
        to match. The session variable will be silently
        dropped and marked for deletion. If the server
        does not set a new value into that session var
        it will be deleted upon response.
        
"""
__all__ = ['MemorySession', 'CookieSession']
import base64 

try:
    import cPickle as pickle
except ImportError:
    import pickle

from event import Event
from Cookie import Morsel
from utils import quick_hash

class Session:
    
    __session_id = None
    
    def __init__(self):
        self.on_start = Event()
        self.on_close = Event()
    
    def clear(self):
        self.on_close()
    
    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default
    
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
    
class CookieSession(Session):
    
    def __load_cookie(self, cookies, cookie):
        
        key_name = cookie.replace("session__", "")
        key_value = cookies[cookie]
        
        # We need to get the signature off the value. I didn't know
        # what a good delimiter was so I chose '.'
        try:
            key_sig, key_value = key_value.split('.')
        except:
            self.__data[key_name] = ('', True)
            return
        
        # We hash after base64 encoding so we need to validate
        # before base64 decoding.
        our_sig = quick_hash(self.id, self.secret_key, key_value)
        
        if our_sig == key_sig:
            key_value = base64.b64decode(key_value)
            key_value = pickle.loads(key_value)
            self.__data[key_name] = (key_value, False)
        
        # else we assume that the cookie was an attack.
        # we will enter it's name into the dict but set it
        # to be deleted in the response.
        else:
            self.__data[key_name] = ('', True)
    
    def __load_cookies(self, cookies):
        
        for cookie in cookies.keys():
            if cookie.startswith('session__'):
                self.__load_cookie(cookies, cookie)
                
    
    def __init__(self, session_id, cookies, options):
        Session.__init__(self)
        self.options = options
        self.secret_key = options['secret_key']
        self.__data = dict()
        self.id = session_id
        self.__load_cookies(cookies)
        
    def iterkeys(self):
        # As we iterate keys, check to see if they aren not
        # also set as deleted.
        for key in self.__data.keys():
            if key in self:
                yield key
                
    def keys(self):
        return [x for x in self.iterkeys()]
        
    def __contains__(self, name):
        """ This returns true if the key exists and is not
        marked as having been deleted. """
        if name in self.__data:
            (val, deleted) = self.__data[name]
            if not deleted:
                return True
            
        return False        
        
    
    def __getitem__(self, name):
        value, deleted = self.__data[name]
        if deleted:
            raise KeyError(name)
        return value
    
    def __setitem__(self, name, val):
        self.__data[name] = (val, False)
        
    def __delete__(self, name):
        self.__data[name] = ('', True)
        
    def to_cookies(self):
        
        for key, (value, deleted) in self.__data.iteritems():
            
            morsel = Morsel()
            morsel.key = "session__%s" % key
            
            if not deleted:
                
                value = pickle.dumps(value)
                value = base64.b64encode(value)
                sig = quick_hash(self.id, self.secret_key, value)
                value = ".".join((sig, value))
                
            else:
                value = 'no-value'
                morsel['expires'] = -3600
                # Sets the cookie to expire in the past.
            
            
            morsel.coded_value = morsel.value = value
            
            # This optionally sets the cookie's timeout till
            # deletion.
            if 'timeout' in self.options:
                timeout = self.options['timeout']
                morsel['expires'] = timeout
                morsel['max-age'] = timeout
                
            morsel['path'] = '/'
            
            yield morsel
        
        


class MemorySession(Session):
    
    def __init__(self, session_dict):
        Session.__init__(self)
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
        
    
    
    
    
    
    
    

