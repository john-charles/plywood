from requests import Request
from URLDispatcher import URLDispatcher
from exceptions import ServerException, Server500Exception

class WSGIHandler:
    
    def __init__( self, urllist ):    
        self.urldispatcher = URLDispatcher( urllist )
        
    
    def __call__( self, environ, response_callback ):
        
        request = Request( environ )
        
        try:
            
            response = self.urldispatcher.call( request.getPathInfo()[1:], request )
                       
            if not response: response = ""
            status = "200 OK"
            response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response)))
            ]
            
        except ServerException, e:
            response = e.toHtml().strip()
            
            status = e.getStatus()
            response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response)))
            ]
        except Exception, e:
            
            e = Server500Exception(e.message, request.getPathInfo() )
            
            response = e.toHtml().strip()
            
            status = e.getStatus()
            response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response)))
            ]
        
            
            
            
        response_callback(status, response_headers)
        return [ response ]
        