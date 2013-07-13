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
__all__ = ['run_method']
import os, sys
from watcher import start_watcher

DO_MAIN_ENV = "__plywood_reloader_do_main__"
DO_P_RELOAD = 12

def start_with_watch_thread(method, *args, **kw):
    
    start_watcher(lambda: os._exit(DO_P_RELOAD))
    # This method should be a long running call
    # like a server never ending while loop!
    #thread.start_new(method, args, kw)
    method(*args, **kw)
    

def start_reloader():
    
    while True:
        # Until the child process fails with a different error code, restart it!        
        args = [sys.executable] + sys.argv
        
        if sys.platform.startswith('win'):
            args = ['"%s"' % arg for arg in args]
        
        c_env = os.environ.copy()
        c_env[DO_MAIN_ENV] = "true"
        
        try:
            exit_code = os.spawnve(os.P_WAIT, sys.executable, args, c_env)
            if exit_code != DO_P_RELOAD: return exit_code
        except KeyboardInterrupt:
            return 0
            
        
    

def run_method(method, *args, **kw):
    
    if os.environ.get(DO_MAIN_ENV) == "true":
        start_with_watch_thread(method, *args, **kw)
        os._exit(0)
    else:
        start_reloader()
        
    
    
    
    
        
        
    