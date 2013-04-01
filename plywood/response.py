
class ResponseException(Exception):pass
class Response:
    
    cookies = None
    headers = None
    
    def __init__(self, request):
        self.cookies = dict()
        self.headers = dict()
        self.request = request
    
    def SetCookie(self, name, value, domain=None, path=None, expires=None, secure=False, httponly=True):
        if not self.cookies:
            raise ResponseException("Init Not Called")
        self.cookies[name] = (value,
            {'domain' : domain, 'path' : path, 'expires' : expires, 'secure' : secure, 'httponly' : httponly})
            
    def GetCookie(self, name):
        if not self.cookies: 
            raise ResponseException("Init Not Called")
        return self.cookies[name]
    
    def Cookies(self):
        if not self.cookies:
            raise ResponseException("Init not Called")
        return self.cookies.keys()
    
    def __CheckHeaders(self):
        if not self.headers:
            raise ResponseException("Init not called")
    
    def SetHeader(self, name, value):
        self.__CheckHeaders()
        self.headers[name] = value
        
            
    def GetHeader(self, name):
        self.__CheckHeaders()
        return self.headers[name]
        
    def Headers(self):
        self.__CheckHeaders()
        return self.headers.keys()
    
    def GetHeaders(self):
        self.__CheckHeaders()
        
        cookie_list = list()        
        
        for name in self.Cookies():
            value, attrs = self.GetCookie(name)
            attr_list = list(("=".join((name, value)))
                        
            for attr_name, attr_val in attrs.iteritems():
                if attr_val:
                    attr_list.append("=".join((attr_name, attr_val))
            
            cookie_list.append(";".join(attr_list))
            
        cookie_list = ",".join(cookie_list)
        
        if cookie_list:
            self.headers['Set-Cookie'] = cookie_list
        
        return [(name, value) for name, value in self.headers.iteritems()]
    
    def GetBody(self):
        raise NotImplemented("GetBody must be implemented by inheriting response type!")
    
    def GetRequest(self):
        return self.request
    
    def GetStatus(self):
        raise NotImplemented("GetStatus must be implemented by inheriting response type!")
    
    
class PageResponse(Response):
    
    def __init__(self, request, page):
        Response.__init__(self, request)
        self.page = page.encode("utf-8") if isinstance(page, unicode) else str(page)
        
    def GetBody(self):
        return [self.page]
    
    def GetStatus(self):
        return "200 OK"
    
class RedirectResponse(Response):
    
    def __init__(self, request, redirect_url):
        Response.__init__(self, request)
        self.SetHeader("Location", redirect_url)
        
    def GetBody(self):
        return []
    
    def GetStatus(self):
        # TODO: This should check the request, if the request
        #   does not come from a modern browser it should send
        #   a 302, rather than a 303.
        return "303 See Other"
    
class PermanentRedirectResponse(RedirectResponse):
    
    def __init__(self, request, redirect_url):
        RedirectResponse.__init__(self, request, redirect_url)
        
    def GetStatus(self):
        return "301 Moved Permanently"
    
class StreamResponse(Response):
    
    def __init__(self, request, resp_iterable):
        Response.__init__(self, request)
        self.resp_iterable = resp_iterable
        
    def GetBody(self):
        return self.resp_iterable
    
    def GetStatus(self):
        return "200 OK"
    
class NotFoundResponse(PageResponse):
    
    def __init__(self, request, page):
        PageResponse.__init__(self, request, page)
        
    def GetStatus(self):
        return "404 Not Found"
    
class PermissionDeniedResponse(PageResponse):
    
    def __init__(self, request, page):
        PageResponse.__init__(self, request, page)
        
    def GetStatus(self):
        return "403 Forbidden"
        
        
class HeadResponse(Response):
    
    def __init__(self, request):
        Response.__init__(self, request)
        
    def GetBody(self):
        return []
    
class NotModifiedResponse(HeadResponse):
    
    def __init__(self, request):
        HeadResponse.__init__(self, request)
        
    def GetStatus(self):
        return "304 Not Modified"
    
class ServerErrorResponse(PageResponse):
    
    def __init__(self, request, page):
        PageResponse.__init__(self, request, page)
        
    def GetStatus(self):
        return "500 Internal Server Error"
    
        

