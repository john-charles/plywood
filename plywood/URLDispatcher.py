#!/usr/bin/env python
import re
from exceptions import Server404Exception as Plywood404Exception, Server403Exception, Server500Exception

class MethodNotCallableException(Exception):pass
class URLDispatcher:
    
    def __init__( self, urllist ):
        self.urllist = urllist
        
    def call( self, path, environ, urllist=None, global_kwargs={} ):
        
        if urllist == None: urllist = self.urllist        
        for pattern, call, kwargs in urllist:
            
            m = pattern.match( path )
            if m:
                
                kwargs = kwargs.copy()
                kwargs.update( global_kwargs )
                kwargs.update( m.groupdict() )
                
                if isinstance( call, tuple ):
                    return self.call( path.replace( m.group(), ""), environ, call, kwargs )
                    
                else:
                    if hasattr(call,'is_view'):
                        return call( environ, **kwargs )
                    else:
                        raise Server500Exception(
                            'method "%s" is not decorated by @view' % call.__name__,
                            environ.getPathInfo()
                        )
        
        raise Plywood404Exception("Could not find path!", environ.getPathInfo() )