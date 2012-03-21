#! /usr/bin/env python
import cgi
from wsgiref.simple_server import make_server

GETTER = """
    %(key)s = %(val)s
        
"""

def application(environ, start_response):

   response_body = str()
   
   for key in sorted(environ.keys()):
       response_body += cgi.escape(GETTER % {'key':key,'val':environ[key]}) + "<br>"

   # Response_body has now more than one string
   response_body = ['<doctype html><html><body>',
                    response_body,
                    #'<h1>%s</h1>' % environ['wsgi.input'].read(int(environ.get("CONTENT_LENGTH"))),
                    '<form method="POST" action="/?someq=var">',
                    '<input type="text" name="user">',
                    '<input type="test" name="val2">',
                    '<input type="submit" value="submit">',
                    '</form>',
                    '</body></html>']

   # So the content-lenght is the sum of all string's lengths
   content_length = 0
   for s in response_body:
      content_length += len(s)

   status = '200 OK'
   response_headers = [('Content-Type', 'text/html'),
                  ('Content-Length', str(content_length)),
                  ] #('Set-Cookie',"TestCookie=MyTestCookie")
   start_response(status, response_headers)

   return response_body

httpd = make_server('localhost', 8051, application)
while True:
    httpd.handle_request()