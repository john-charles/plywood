#! /usr/bin/env python
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
    
    
"""
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    setup_testing_defaults(environ)
    
    if environ['REQUEST_METHOD'] == 'POST':
        leng = environ['CONTENT_LENGTH']
        mpt_file = open("Multipart-form.txt","wb")
        mpt_file.write(environ['wsgi.input'].read(int(leng)))
        mpt_file.close()

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