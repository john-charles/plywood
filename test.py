#! /usr/bin/env python

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    setup_testing_defaults(environ)
    
    if environ['REQUEST_METHOD'] == 'POST':
        leng = environ['CONTENT_LENGTH']
        print environ['wsgi.input'].read(int(leng))

    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    
    keys = environ.keys()
    keys.sort()
    
    ret = list()
    ret.append("<html><body>")
    ret.append('<a href=".">This page</a>')
    
    ret.append('<form method="POST" action="." enctype="multipart/form-data">')
    ret.append('<input type="file" name="my_file">')
    ret.append('<input type="text" name="age">')
    ret.append('<input type="text" name="age">')
    ret.append('<input type="text" name="age">')
    ret.append('<input type="submit" value="Submit">')
    ret.append('</form>')
    
    ret.extend(["%s: %s<br>" % (key, environ[key])
           for key in keys])
    ret.append("</body></html>")
    return ret

httpd = make_server('', 8000, simple_app)
print "Serving on port 8000..."
httpd.serve_forever()


#if __name__ == '__main__':
    
    #application = WSGIHandler( urllist )

    #httpd = make_server('localhost', 8051, application)
    #while True:
        #httpd.handle_request()