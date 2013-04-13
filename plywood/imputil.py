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
import traceback, sys

def import_entity(name):
    
    # This is one of the most frustrating pieces of code to write...
    path = None
    
    for part in name.split("."):
        if not path: path = part
        else: path = ".".join((path, part))
        try:
            m = __import__(path)
        except ImportError, e:
            missing_name = e.message.split(" ")[-1]

            if missing_name != part:
                traceback.print_exc(file=sys.stderr)
                sys.exit(1)
    
    if name.count(".") == 0:
        return m
    
    else:
        tail = name.replace(name.split('.')[0] + ".","")
        for part in tail.split("."):

            if hasattr(m, part):
                m = getattr(m, part)
            else:
                raise ImportError("No object %s" % name)
        
        return m


