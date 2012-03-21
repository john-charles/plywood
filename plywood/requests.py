import hashlib, uuid, time
from Cookie import Cookie
from hashlib import sha256
from base64 import b16encode, b16decode
from datetime import datetime, timedelta
from urlparse import parse_qsl, urlparse
from exceptions import Server403Exception

def quickHash( *args ):

    sha = hashlib.sha256()

    for arg in args:
        sha.update( str(arg) )

    return sha.hexdigest()


class WSGIRequest:
    
    def __init__(self,environ):
        self.environ = environ
        self.__content_read = 0
        self.__resp_headers = {}
        
    def getScriptName(self):
        return self.environ.get("SCRIPT_NAME","")
        
    def getPathInfo(self):
        return self.environ.get("PATH_INFO","")
        
    def getContentType(self):
        return self.environ.get("CONTENT_TYPE","")
        
    def getContentLength(self):
        length = self.environ.get("CONTENT_LENGTH")
        if length: return int(length)
        else: return 0
        
    def getServerName(self):
        return self.environ.get("SERVER_NAME","")
        
    def getServerPort(self):
        return self.environ.get("SERVER_PORT","")
        
    def getServerProtocol(self):
        return self.environ.get("SERVER_PROTOCOL","")
        
    def getRemoteHost(self):
        return self.environ.get("REMOTE_HOST","")
        
    def getRemoteAddr(self):
        forwarded_for = self.environ.get("HTTP_X_FORWARDED_FOR","")
        if forwarded_for:
            return forwarded_for.split()[0]
        else:
            return self.environ.get("REMOTE_ADDR","")
        
        
    def __env_to_head(self,key):
        return key.replace('HTTP_','').capitalize().replace('_','-')
        
    def __head_to_env(self,key):
        return "HTTP_%s" % key.upper().replace('-','_')
        
    def __allHeaders(self):
        
        for key in self.environ.keys():
            if key.startswith("HTTP_"):
                yield self.__env_to_head(key)
                
    def allHeaders(self):
        return [ x for x in self.__allHeaders() ]
        
    def getHeader(self,key):
        key = self.__head_to_env(key)
        return self.environ.get(key,"")
        
    def hasHeader(self, key):
        key = self.__head_to_env(key)
        return self.environ.has_key(key)
        
    def allHeadersIter(self):
        
        for header in self.__allHeaders():
            yield (header, self.getHeader( header ))
    
    def _reader( self, length=None ):
        
        if length == None: length = self.getContentLength()
        
        max_length = self.getContentLength()
        max_left = max_length - self.__content_read
        
        if max_left > 0:
            if max_left > length:
                actual_read = length
            else:
                actual_read = max_left
                
            reader = self.environ.get('wsgi.input')
            buff = reader.read( actual_read )
            self.__content_read = self.__content_read + actual_read
            return buff
        else:
            return ''
            
    def addHeader( self, name, value ):        
        self.__resp_headers[ name ] = value
        
class CookiedRequest(WSGIRequest):
    
    __cookes = None
    
    def allCookies(self):
        if self.__cookes == None:
            cookies = self.getHeader("Cookie")
            self.__cookes = Cookie( cookies )
        return self.__cookes.copy()
        
    def hasCookie(self, key):
        cookies = self.allCookies()
        return cookies.has_key(key)
        
    def getCookie(self, key):
        cookies = self.allCookies()
        return cookies.get(key)
        
        
            
class SubmissionRequest(CookiedRequest):
    
    __secret_key = "Secret Key"
    
    def getMethod(self):
        return self.environ.get("REQUEST_METHOD","GET")
        
    def isGet(self):
        return self.getMethod() == 'GET'
        
    def isPost(self):
        return self.getMethod() == 'POST'
        
    def __qs_to_dict(self,qs):
        result = dict()
        for key, val in parse_qsl(qs):
            result[ key ] = val
        return result
        
        
    def getQuery(self):
        query = self.environ.get("QUERY_STRING","")
        return self.__qs_to_dict( query )
        
    def __get_source_domain(self):
        
        if self.hasHeader("Origin"):
            origin = self.getHeader("Origin")
        else:
            origin = self.getHeader("Referer")
        
        if not origin:
            raise Server403Exception("Could not reliably get an origin, or referer header, aborting Post")
        return urlparse( origin ).netloc
        
        
    def __get_times(self):
        
        now = datetime.now()
        now = datetime(year=now.year,month=now.month,day=now.day,hour=now.hour)
        old = now - timedelta(minutes=30)
        fmt = "%H %M"
        return (now.strftime(fmt), old.strftime(fmt))
        
        
        
    def getCSRFTokenSet(self):
        
        remote_addr = self.getRemoteAddr()
        
        if self.isGet():
            domain = self.getHeader("Host")
        elif self.isPost():
            domain = self.__get_source_domain()            
            
        now, old = self.__get_times()
        now_token = quickHash( remote_addr, domain, now, self.__secret_key )
        old_token = quickHash( remote_addr, domain, old, self.__secret_key )
        
        return ( now_token, old_token )
        
    def getCSRFCurrentToken(self):
        return self.getCSRFTokenSet()[0]
        
          
    def getCSRFTokenField(self):
        return '<input type="hidden" name="csrf_token" value="%s">' % self.getCSRFCurrentToken()
        
    def getPost(self):
        
        if self.isPost():
            post_data = self._reader()
            result = self.__qs_to_dict( post_data )
        else:
            result = dict()
            
        if result.get("csrf_token","") in self.getCSRFTokenSet():
            return result.copy()
        else:
            raise Server403Exception("CSRF Token invalid!", self.getPathInfo())
        
         
        
    def getRequest(self):
        
        request = self.getQuery()
        request.update( self.getPost() )
        return request
        
        
class Request(SubmissionRequest):
    pass
        
            

        
        
    
    