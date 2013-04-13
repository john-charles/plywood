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
__all__ = ['url','include','Urls']

import re, inspect
from forms import Form
from views import View
from exceptions import *
from imputil import import_entity

# NOTE: I did not comment this code when I wrote it, 
#   so it took me longer than I wanted to figure out.
#   so I will describe it now.
#
#   When a user creates a url in the urllist they
#   call this function for each url. This converts
#   the url into the proper set of re, call, kwargs.
#
def url( pattern, call, **kwargs ):   
    if isinstance(call, str):
        call = import_entity(call)
    
    if not callable(call):
        if not isinstance(call, tuple):
            raise TypeError("A function, or callable class is required!")
    
    return (re.compile( pattern ), call, kwargs)

    
# This will include a urls list, this can do an
#   inline include, or a text based/import include.
def include(urllist_name):
    if isinstance(urllist_name, str):
        return import_entity(urllist_name)
    elif isinstance(urllist_name, tuple):
        return urllist_name
    else:
        raise TypeError("A tuple is expected!")
    
def Urls(*urllist):
    
    # Adds support for the django style first arg is a 
    # namespace prefix, to plywood urllists.
    if len(urllist) > 0:
        if isinstance(urllist[0], (str, unicode)):
            namespace = urllist[0]
            new_urllist = list()
            
            # Since we have a namespace prefix we can now
            #   apply it to all calls represented as strings.
            for pattern, call, kwargs in urllist[1:]:
                if isinstance(call, str):
                    call = ".".join(namespace, call)
                new_urllist.append((pattern, call, kwargs))
            
            urllist = tuple(new_urllist)
    
    return include(urllist)


class URLDispatcher:
    
    def __init__( self, urllist):
        self.urllist = include(urllist)
        
    def call(self, path, environ, urllist=None, global_kwargs={}):
        
        if urllist == None: urllist = self.urllist        
        for pattern, call, kwargs in urllist:
            
            m = pattern.match(path)
            if m:
                
                kwargs = kwargs.copy()
                kwargs.update( global_kwargs )
                kwargs.update( m.groupdict() )
                
                # If the call is actually a sub-urllist then recursively process
                # that urllist. 
                if isinstance(call, tuple):
                    return self.call(path.replace(m.group(), ""), environ, call, kwargs)
                    
                # If the call is a class then the class should be instantiated
                elif inspect.isclass(call):
                    
                    call_instance = call(environ)
                    
                    # if the call instance is a form we need to first 
                    # check the request type and if necessary, validate
                    # the form.
                    if isinstance(call_instance, Form):
                        if environ.is_post():
                            call_instance.validate(environ.post)
                            
                    if isinstance(call_instance, (View, Form)):
                        response = call_instance(**kwargs)
                        del call_instance; return response
                            
                    else:
                        raise Server500Exception("Class is not a View instance!",
                            environ.path_info)
                
                elif callable(call):
                    return call(environ, **kwargs)
                
                else:
                    raise Server500Exception('The "call" is not callable!','Yeiks')
        
        raise Server404Exception("Could not find path!", environ.path_info)
    
