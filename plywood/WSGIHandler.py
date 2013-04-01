from requests import Request
from URLDispatcher import URLDispatcher
from response import Response, ResponseRedirect
from exceptions import ServerException, Server500Exception

class WSGIHandler:
    
    def __init__(self, urllist, middleware=tuple(), forbidden_redirect=None):    
        self.urldispatcher = URLDispatcher(urllist, middleware=middleware)
        self.forbidden_redirect = forbidden_redirect
        
    
    def __call__( self, environ, response_callback ):
        
        request = Request( environ )
        
        try:
            
            response = self.urldispatcher.call(request.getPathInfo()[1:], request)
            
            if isinstance(response, Response):
                status = response.status
                response_headers = response.getHeaders()
                
            else:
                raise Exception("View failed to resturn a valid Response object.")
            
        except ServerException, e:
            response = Response(e.toHtml().strip(), request)
            
            status = e.getStatus()
            response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response)))
            ]
            
        except Exception, e:
            
            e = Server500Exception(e.message, request.getPathInfo())
            
            response = Response(e.toHtml().strip(), request)
            
            status = e.getStatus()
            response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response)))
            ]
        
            
            
            
        response_callback(status, response_headers)
        return response.getIterator()

        