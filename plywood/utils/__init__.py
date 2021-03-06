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
__all__ = ['dev_server','static_files']

import hashlib
from os.path import join, exists
from plywood.exceptions import Server404Exception
from plywood import __version__

from reloader import run_method

def quick_hash( *args ):

    sha = hashlib.sha256()

    for arg in args:
        sha.update(str(arg))

    return sha.hexdigest()

        
def dev_server(application, bindhost='localhost', bindport=8050):
    
    from wsgiref.simple_server import make_server
    
    def server_loop():
        
        httpd = make_server(bindhost, bindport, application)
        
        print """Plywood Copyright (C) 2013  John-Charles D. Sokolow
        This program comes with ABSOLUTELY NO WARRANTY; 
        for details see COPYING and COPYING.LESSER distributed
        with this library or visit <http://www.gnu.org/licenses/>
        """
        
        info = (__version__, bindhost, bindport)
        print "Plywood version '%s' listening on http://%s:%s/" % info
        print "Press 'Ctrl+C' to quit!" 
    
        try:
            while True:
                httpd.handle_request()
        
        except KeyboardInterrupt:        
            print "\nShutting down..."
    
    # This puts the server loop into a subprocess and
    # starts the reloader thread!
    run_method(server_loop)
        
        


            
