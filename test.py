#! /usr/bin/env python

from wsgiref.simple_server import make_server
#from plywood import WSGIHandler

from plywood.tools import url, include, Urllist, public
from plywood.decorators import view
from plywood import WSGIHandler

@view( auth_method=public )
def testcall( request, **kwargs ):   
    return "<h1>Hi</h1>"
    
    
@view( auth_method=public )
def posttest( request, **kwargs ):
    
    if request.isGet():
        
        return """<form method="POST" action="/post/">
    %(csrf_token)s
    <input type="text" name="test_input">
    <input type="submit" value="submit">
</form>""" % { 'csrf_token': request.getCSRFTokenField() }

    elif request.isPost():
        return """<h1>You Posted:</h1>
        <h3>%s</h3>""" % request.getPost()['test_input'] 

urllist = Urllist(
    url(r'^$', testcall ),
    url(r'^post/$', posttest ),

)



if __name__ == '__main__':
    
    application = WSGIHandler( urllist )

    httpd = make_server('localhost', 8051, application)
    while True:
        httpd.handle_request()