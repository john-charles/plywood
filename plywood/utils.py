__all__ = ['dev_server','static_files']

import hashlib
from os.path import join, exists
from exceptions import Server404Exception

def quick_hash( *args ):

    sha = hashlib.sha256()

    for arg in args:
        sha.update(str(arg))

    return sha.hexdigest()

        
def dev_server(application, bindhost='localhost', bindport=8051):
    
    from wsgiref.simple_server import make_server
    
    httpd = make_server(bindhost, bindport, application)
    
    try:
        while True:
            httpd.handle_request()
    
    except KeyboardInterrupt:        
        print "\nShutting down..."
        
    return True
        
        


            
