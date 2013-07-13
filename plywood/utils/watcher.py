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
__all__ = ['start_watcher']

import os, sys, time
from threading import Thread

class ChangeWatcher:
    
    on_change_event = None
    
    def fire_on_change_event(self):
        if self.on_change_event:
            self.on_change_event()
    
class PollingChangeWatcher(ChangeWatcher, Thread):
    
    src_file_list = dict()
    is_win = sys.platform.startswith('win')
    
    def __init__(self, on_change_event):
        Thread.__init__(self)
        self.on_change_event = on_change_event
    
    def get_mtime(self, path):
        """This returns the proper mtime of the path
            specified!"""
        stat = os.stat(path)
        if self.is_win:
            return stat.st_mtime - stat.st_ctime
        else:
            return stat.st_mtime
        
    def get_src_file(self, c_file):
        ''' This takes the name of a python code file and returns
            the matching python source file!'''
        if c_file.endswith(".pyc") or c_file.endswith(".pyo"):
            return c_file[:-1]
        if c_file.endswith("$py.class"):
            return c_file[:-9] + ".py"
        if c_file.endswith('.py'):
            return c_file
        
    def has_code_changed(self):
        
        for module in sys.modules.values():
            try:
                m_file = getattr(module, "__file__")
            except AttributeError, e:
                # This mean's it's a built in which we don't
                # care about anyway!
                continue
            
            s_file = self.get_src_file(m_file)
            
            if not s_file or not os.path.exists(s_file):
                continue
            
            sf_mtime = self.get_mtime(s_file)
            
            if s_file not in self.src_file_list:
                self.src_file_list[s_file] = sf_mtime
            else:
                if sf_mtime != self.src_file_list[s_file]:
                    print "A file change has ocurred!"
                    return True
            
        return False
        
    def run(self):
        
        while True:
            if self.has_code_changed():
                self.fire_on_change_event()
            # This is the same interval as django and it
            # seems to work!
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                return 0
            
def start_watcher(on_change_event):
    '''This get's the best change watcher supported by the platform
        falling back to polling if no other watcher can be found!'''
    # Since I've only implemented polling change watcher, I'll
    # just return that!
    w = PollingChangeWatcher(on_change_event)
    w.start()