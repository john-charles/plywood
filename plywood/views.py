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
    
    
    
    