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

class ServerException(Exception):
    
    def __init__(self, mesg, path, reason, status ):
        Exception.__init__(self, mesg)
        self.path = path
        self.reason = reason
        self.status = status
        
    def GetStatus(self):
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
    