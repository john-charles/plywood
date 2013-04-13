from exceptions import *
from urls import URLDispatcher
from imputil import import_entity
from http import Request, Response, ServerErrorResponse, LinkResponse

class WSGIHandler:
    
    def __init__(self, urllist, wrappers=None, options={}):    
        self.urldispatcher = URLDispatcher(urllist)
        self.options = options
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
                
        
        response_callback(response.GetStatus(), response.GetHeaders())
        return response.GetBody()

        