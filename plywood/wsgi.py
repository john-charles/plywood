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
from exceptions import *
from urls import URLDispatcher
from imputil import import_entity
from http import Request, Response, ServerErrorResponse, LinkResponse

class WSGIHandler:
    
    def __init__(self, urllist, wrappers=None, options={}):    
        self.urldispatcher = URLDispatcher(urllist)
        self.options = options
        
        if 'secret_key' not in options:
            raise ConfigurationException("Error, a secret_key must be specified!")
        
        self.middleware = self.__init_middlware(wrappers)
        
        
    def __init_middlware(self, wrappers):
        
        middleware = list()
        for wrapper, wopts in wrappers:
            
            options = self.options.copy()
            options.update(wrappers.default_options)
            options.update(wopts)
            
            if isinstance(wrapper, str):
                wrapper = import_entity(wrapper)
            middleware.append(wrapper(options))
        
        return middleware
        
    def process_request(self, request):
        
        called_middleware = list()
        
        for middleware in self.middleware:
            try:
                response = middleware.request(request)
                if isinstance(response, Response):
                    self.process_response(called_middleware, response)
                    return response
            
            except NotImplemented:
                pass
            
            finally:
                    called_middleware.append(middleware)
                    
        return called_middleware    
        
        
    def process_response(self, called_middleware, response):
        
        while len(called_middleware) > 0:
            middleware = called_middleware.pop()
            middleware.response(response)
            
    def __call__(self, environ, response_callback):        
        # Turn the environment object into an actual request object.
        environ['options'] = self.options
        request = Request(environ)
        
        try:
            
            # Call request middleware. If the response is an
            #     Response object then return that, assume that
            #     a middleware objected and responded itself.
            called_middleware = self.process_request(request)
            if isinstance(called_middleware, Response):
                return called_middleware
                    
            try:
                
                response = self.urldispatcher.call(request.path_info[1:], request)
                
                if not isinstance(response, Response):
                    raise Server500Exception(
                        "The view did not return a Response object!",
                        request.path_info
                    )
                
            except Server403Exception, e:
                if 'login_url' in self.options:
                    response = LinkResponse(request, self.options['login_url'],
                        query={'next': request.path_info})
                else:
                    response = ServerErrorResponse(request, e)

            except ServerException, e:
                response = ServerErrorResponse(request, e)
                
            # The drawback to this design is that when critical/unhandled
            # exceptions ocurr the response middleware is not called.
            self.process_response(called_middleware, response)
            
        except Exception, e:
            
            e = Server500Exception(e.message, request.path_info)
            response = ServerErrorResponse(request, e)
            if self.options.get('print_exceptions', False):
                print response.exception.traceback_text
                
        
        response_callback(response.get_status(), response.get_headers())
        return response.get_body()

        