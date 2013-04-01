import traceback

exception_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>%(reason)s!</title>
    </head>
    <body>
        <h1>%(reason)s!</h1>
        URL: "%(path)s" is inaccessable!<br>
        please contact the server administrator for help!<br>
        %(message)s<br>
        <br>
        %(traceback)s<br>
    </body>
</html>
"""

class ServerException(Exception):
    
    def __init__(self, mesg, path, reason, status ):
        Exception.__init__(self, mesg)
        self.path = path
        self.reason = reason
        self.status = status
        
    def getStatus(self):
        return self.status
        
    def toHtml(self):
        
        return exception_html % {
            'reason':self.reason,
            'path':self.path,
            'message':self.message,
            'traceback': traceback.format_exc().replace('\n','<br>\n').replace('  ','&nbsp;'* 4)
        }

class Server404Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '404 Page Not Found', '404 Error')
        
class Server403Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '403 Forbidden', '403 Error')
        
class Server500Exception(ServerException):
    
    def __init__(self, mesg, path):
        ServerException.__init__(self, mesg, path, '500 Internal Error', '500 Error')
    