#!/usr/bin/env python
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

plywood.http:
    plywood.http.Request      -- A class that wraps a WSGI environment.
    plywood.http.Response     -- A class that a view must return with cookies and headers
                                    and everything else to be sent to the client.
                                    
"""
__all__ = ['Request','Response']

import json
from cookies import CookieList
from Cookie import SimpleCookie
from urlparse import parse_qsl, urlparse

# Local imports
from query import Query
from utils import quick_hash
from exceptions import Server403Exception

class Request:
    
    def __init__(self,environ):
        self.environ = environ
        self.__content_read = 0
        self.__headers = self.__process_headers()
        self.__cookies = self.__process_cookies()
        self.__secret_key = environ['options']['secret_key']
        
    def __process_headers(self):
        headers = dict()
        
        hton = lambda x: x.replace("HTTP_","").capitalize()
        
        for name in self.environ.keys():
            if name.startswith("HTTP_"):
                headers[hton(name)] = self.environ[name]
                
        return headers
    
    def __process_cookies(self):
        simple_cookie = SimpleCookie(self.headers.get("Cookie",{}))
        cookies = dict()
        
        for cookie in simple_cookie.itervalues():            
            cookies[cookie.key] = cookie.value
        
        return cookies
            
    
    @property
    def cookies(self):
        return self.__cookies
        
    @property
    def content_length(self):
        length = self.environ.get("CONTENT_LENGTH")
        try:
            return int(length)
        except TypeError:
            return 0
        
    @property
    def content_type(self):
        return self.environ.get("CONTENT_TYPE","")
    
    # https://www.owasp.org/index.php/Cross-Site_Request_Forgery_%28CSRF%29_Prevention_Cheat_Sheet
    @property
    def csrf_token(self):
        # This get's a csrf_token using available
        # data. The purpouse of this csrf token is to
        # ensure that any post data came from a page that
        # was loaded from this server.
        if not hasattr(self, "__csrf_token"):
            # if the request is a get request, we just
            # use the host that was requested by the 
            # user, since the netloc of host should
            # be the netloc of the referer or origin
            # headers of the post request.
            if self.is_get:
                origin = self.headers["Host"]
            # Else we just grab the netloc of the origin
            # or referer header.
            else:
                if "Origin" in self.headers:
                    origin = self.headers["Origin"]
                elif "Referer" in self.headers:
                    origin = self.headers["Referer"]
                else:
                    raise Server403Exception("Could not reliably determin origin")
            
                origin = urlparse(origin).netloc
                
            remote_addr = self.remote_addr
            secret_key = self.__secret_key
            
            # Create the csrf token by hashing the origin, the remote
            # address of the request and our secret key. This key will
            # then be compared to the "csrf_token" value in the post.
            # only if the form came from this domain, and was sent to
            # this remote host will the form validate. 
            self.__csrf_token = quick_hash(origin, remote_addr, secret_key)
            
        return self.__csrf_token
    
    @property
    def csrf_token_field(self):        
        field = """<input type="hidden" name="csrf_token" value="%s">"""
        return field % self.csrf_token
    
    @property
    def headers(self):
        return self.__headers
    
    @property
    def is_get(self):
        return self.method == "GET"
    
    @property
    def is_post(self):
        return self.method == "POST"
    
    @property
    def method(self):
        return self.environ.get("REQUEST_METHOD","GET")
    
    @property
    def path_info(self):
        return self.environ.get("PATH_INFO","")
    
    def __reader(self, length=None):
        
        if length == None: length = self.content_length
        
        max_length = self.content_length
        max_left = max_length - self.__content_read
        
        if max_left > 0:
            if max_left > length:
                actual_read = length
            else:
                actual_read = max_left
                
            reader = self.environ.get('wsgi.input')
            buff = reader.read(actual_read)
            self.__content_read = self.__content_read + actual_read
            return buff
        else:
            return ''        
        
    def __loadreader(self):
        # For some reason this is getting called
        # multiple times and it ends up returning
        # and empty query after the first call.
        if self.__content_read == 0:
            self.__reader_result = Query(self.__reader,
                self.content_type, self.content_length)
            
        return self.__reader_result
        
    @property
    def post(self):
        
        if self.is_post:
            post_data = self.__loadreader()
            
            if post_data['csrf_token'] != self.csrf_token:
                raise Server403Exception("Invalid CSRF Token", self.path_info)
            
            return post_data
        
        else:
            return Query(query_dict=dict())
        
    
    @property
    def query(self):
        return Query(self.environ.get("QUERY_STRING",""))
    
    @property
    def remote_addr(self):
        forwarded_for = self.environ.get("HTTP_X_FORWARDED_FOR","")
        if forwarded_for:
            return forwarded_for.split()[0]
        else:
            return self.environ.get("REMOTE_ADDR","")
    
    @property
    def remote_host(self):
        return self.environ.get("REMOTE_HOST","")
    
    @property
    def request(self):        
        query = self.query
        query.update(self.post)
        return query
    
    @property
    def script_name(self):
        return self.environ.get("SCRIPT_NAME","")
    
    @property
    def server_name(self):
        return self.environ.get("SERVER_NAME","")
    
    @property
    def server_port(self):
        return self.environ.get("SERVER_PORT","")
    
    @property
    def server_protocal(self):
        return self.environ.get("SERVER_PROTOCOL","")
    
    def __del__(self):
        if self.__content_read:
            del self.__reader_result
    
    
class Response:
    
    def __init__(self, request):
        self.__cookies = CookieList()
        self.headers = dict()
        self.request = request
    
    @property
    def cookies(self):
        return self.__cookies
    
    def set_cookie(self, name, value, domain=None, path=None, expires=None, secure=False, httponly=True):
        self.cookies.set_cookie(name, value, path, "", domain, expires, secure, None, httponly)
    
    
    def SetHeader(self, name, value):
        self.headers[name] = value
        
            
    def GetHeader(self, name):
        return self.headers[name]
    
    def Headers(self):
        return self.headers.keys()
    
    def GetHeaders(self):
        
        headers = [(name, value) for name, value in self.headers.iteritems()]
        headers.extend([('Set-Cookie', cookie.OutputString()) for cookie in self.cookies])
        
        #print headers
        
        return headers
    
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
    
class LinkResponse(RedirectResponse):
    
    def __init__(self, request, redirect_url, query={}, hashid=None):
        
        query_list = list()
        
        for key, val in query.iteritems():
            query_list.append("=".join((key, val)))
            
        redirect_url = redirect_url + "?" + "&".join(query_list)
        if hashid: redirect_url = redirect_url = "#" + hashid
        
        RedirectResponse.__init__(self, request, redirect_url)
        
    
class PermanentRedirectResponse(RedirectResponse):
    
    def __init__(self, request, redirect_url):
        RedirectResponse.__init__(self, request, redirect_url)
        
    def GetStatus(self):
        return "301 Moved Permanently"
    
class StreamResponse(Response):
    
    def __init__(self, request, resp_iterable, content_type=None):
        Response.__init__(self, request)
        self.resp_iterable = resp_iterable
        if content_type:
            self.SetHeader("Content-Type", content_type)
        else:
            self.SetHeader("Content-Type", "text/css")
        
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
    
    def __init__(self, request, exc):
        PageResponse.__init__(self, request, exc.ToHTML().strip())
        self.exception = exc
        
    def GetStatus(self):
        return self.exception.GetStatus()
    
class JsonResponse(PageResponse):
    
    def __init__(self, request, json_data):
        page_data = json.dumps(json_data)
        PageResponse.__init__(self, request, page_data)
    
            
        
if __name__ == '__main__':
    
    r = Request({'HTTP_COOKIE':"age=32; httponly=true, name=john; secure=true"})
    
    attrs = dir(r)
    attrs.sort()
    
    for name in attrs:
        print name
        
        
