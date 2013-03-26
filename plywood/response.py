

class Response:
    
    status = "200 OK"
    cookies = None
    
    def __init__(self, html, request=None): 
        
        self.html = str(html)
        self.request = request
        self.cookies = dict()
        
    def getRequest(self):        
        return self.request
        
    def setCookie(self, name, value, domain=None, path=None, expires=None, secure=False, httponly=True):
        self.cookies[name] = (value, {'domain' : domain, 'path' : path, 'expires' : expires, 'secure' : secure, 'httponly' : httponly})
        
    def toHtml(self):
        return self.html
    
    def __len__(self):
        return len(self.html)
    
    def getIterator(self):
        
        if isinstance(self.html, str):
            return (self.html,)
        else:
            return self.html
    
    def getHeaders(self):
        
        default = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(self.toHtml())))
        ]
        
        for name, (value, options) in self.cookies.iteritems():
            default.append(('Set-Cookie','%s=%s;' % (name, value)))
            
        return default
    
class ResponseRedirect(Response):
    
    def __init__(self, url, request):
        self.url = url
        self.request = request
        self.status = "303 See Other"
        self.cookies = dict()
        
    def getHeaders(self):
        
        return [
            ('Location', self.url)
        ]
        
    def getIterator(self):
        return []
                
            