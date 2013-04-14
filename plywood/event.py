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

class Event:
    
    def __init__(self):
        self.call_list = list()
        
    def __iadd__(self, call):
        if not callable(call):
            raise ValueError("Object not callable!")
        self.call_list.append(call)
        return self
    
    def __isub__(self, call):
        try:
            index = self.call_list.index(call)
            self.call_list.pop(index)
        except:
            pass
        return self
        
    def __call__(self, *args, **kw):
        for call in self.call_list:
            call(*args, **kw)