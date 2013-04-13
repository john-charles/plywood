from http import StreamResponse
from os.path import join, exists
from wsgiref.util import FileWrapper
from exceptions import Server403Exception

class View:
    
    def __init__(self, request):
        self.__request = request
        
    @property
    def request(self):
        return self.__request
    
    def __call__(self, **kwargs):
        raise NotImplemented()
    
    
def static_files(request, path, directory_list):
    
    if path.count('..'):
        raise Server403Exception(
            "Cannot view subdirectories or '..'", request.path_info)
    
    if isinstance(directory_list, str):
        directory_list = list([directory_list])
    
    for directory in directory_list:
        
        file_path = join(directory, path)
        if exists(file_path):
            fwrapper = FileWrapper(open(file_path, 'rb'))
            return StreamResponse(request, fwrapper)
    
    pathinfo = repr(directory_list) + " " + path
    raise Server404Exception("Could not find static file", pathinfo)
    
    
    
    