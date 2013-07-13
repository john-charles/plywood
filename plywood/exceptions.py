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
"""
import traceback

exception_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>%(reason)s!</title>
    </head>
    <body style="padding:0px;margin:0px;">
        <h1 style="padding:15px;margin:0px;">%(reason)s!</h1>
        <p style="margin:10px;">
            URL: "%(path)s" is inaccessable!<br>
            please contact the server administrator for help!<br>
            %(message)s<br>
            <br>
            %(traceback)s<br>
        </p>
    </body>
</html>
"""

class ConfigurationException(Exception): pass

class ServerException(Exception):
    
    def __init__(self, mesg, path, reason, status ):
        Exception.__init__(self, mesg)
        self.path = path
        self.reason = reason
        self.status = status
        
    def get_status(self):
        return self.status
        
    def ToHTML(self):
        
        self.traceback_text = traceback.format_exc()
        
        return exception_html % {
            'reason':self.reason,
            'path':self.path,
            'message':self.message,
            'traceback': self.traceback_text.replace('\n','<br>\n').replace('  ','&nbsp;'* 4)
        }

class Server404Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '404 Page Not Found', '404 Error')
        
class Server403Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '403 Forbidden', '403 Error')
        
class Server413Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '413 Request Entity Too Large','413 Request Entity Too Large')
        
class Server500Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '500 Internal Error', '500 Error')
    