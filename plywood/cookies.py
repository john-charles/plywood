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
from Cookie import Morsel

ERROR_NOT_MORSEL = "Values added to CookieLists with '+=' must be of type 'Cookie.Morsel'"

class CookieList:
    
    def __init__(self):
        self.__cookies = dict()
        
    def set_cookie(self, name, value, path=None, comment=None, domain=None,
                   max_age=None, secure=None, version=None, httponly=None):
        
        new_morsel = Morsel()
        new_morsel.key = name
        new_morsel.coded_value = new_morsel.value = value
        
        if max_age:
            # Morsels will take max age and convert it to a date for us.
            new_morsel['expires'] = max_age
            new_morsel['max-age'] = max_age

        
        if path:     new_morsel['path']     = path
        if comment:  new_morsel['comment']  = comment
        if domain:   new_morsel['domain']   = domain
        if secure:   new_morsel['secure']   = secure
        if version:  new_morsel['version']  = version
        if httponly: new_morsel['httponly'] = httponly
        
        self += new_morsel
        
    def del_cookie(self, name):
        if name in self.__cookies:
            del self.__cookies
        
    def __iadd__(self, value):
        if not isinstance(value, Morsel):
            raise ValueError(ERROR_NOT_MORSEL)
        
        self.__cookies[value.key] = value
        return self
        
    def __iter__(self):
        for morsel in self.__cookies.itervalues():
            yield morsel
            
    def __str__(self):
        return "<CookieList%s>" % repr(self.__cookies)