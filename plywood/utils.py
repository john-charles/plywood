__all__ = ['dev_server','static_files']

from os.path import join, exists
from response import StreamResponse
from exceptions import Server404Exception


class SimpleFile:
    
    def __init__(self, file):
        self.file = open(file, "rb")
        
    def __iter__(self):
        
        while True:
            block = self.file.read(4096)
            if not block: break
            yield block
        
        self.file.close()
        
def dev_server(application, bindhost='localhost', bindport=8051):
    
    from wsgiref.simple_server import make_server
    
    httpd = make_server(bindhost, bindport, application)
    
    try:
        while True:
            httpd.handle_request()
    
    except KeyboardInterrupt:        
        print "\nShutting down..."
        
    return True
        
        

def static_files(request, path, directory_list):
    
    if isinstance(directory_list, str):
        directory_list = list([directory_list])
    
    for directory in directory_list:
        
        file_path = join(directory, path)
        if exists(file_path):
            return StreamResponse(request, SimpleFile(file_path))
    
    pathinfo = repr(directory_list) + " " + path
    raise Server404Exception("Could not find static file", pathinfo)
            
