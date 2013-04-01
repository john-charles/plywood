from requests import Request, ServerErrorResponse
from URLDispatcher import URLDispatcher
from response import Response, ResponseRedirect
from exceptions import ServerException, Server500Exception

class WSGIHandler:
    
    def __init__(self, urllist, middleware=tuple(), error_redirects={}):    
        self.urldispatcher = URLDispatcher(urllist, middleware=middleware)
        self.error_redirects = error_redirects       
    
    def __call__(self, environ, response_callback):        
        request = Request(environ)
        
        try:            
            path = request.getPathInfo()[1:]
            response = self.urldispatcher.call(path, request)

        except ServerException, e:
            response = PageResponse(e.toHtml().strip(), request)
            
        except Exception, e:
            
            e = Server500Exception(e.message, request.getPathInfo())
            response = Response(e.toHtml().strip(), request)
            
        
        response_callback(response.GetStatus(), response.GetHeaders())
        return response.GetBody()

        