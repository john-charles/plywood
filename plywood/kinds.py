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

Kinds. I Got the idea for this from the following article.
    http://www.joelonsoftware.com/articles/Wrong.html
    
Although kinds are technically types, their subtly different.
Basically a kind is a standard type, string, int, etc. Which has
a limited set of allowable contents.

This solves my problem if how this framework will manipulate
safe and potentially unsafe user submitted data.

Names
    ss = SimpleString
    cs = ComplexString
    ds = DangerousString

"""
__all__ = ['cs_from_ds','ss_from_ds']

SS_ERROR = "%s strings cannot contain the %s character!"
PERMISSABLE = range(48, 58) + range(65, 91) + range(97, 122)
SS_PERMISSABLE = PERMISSABLE + [32, 95]
CS_PERMISSABLE = SS_PERMISSABLE + [45, 47, 91, 92, 93, 95, 124]
#EM_PERMISSABLE = PERMISSABLE + [64, 46]

def _get_permissable(permissable):    
    return [chr(x) for x in permissable]

def _from(ds_string, silent, permissable, st):
    
    ds_string_list = list(ds_string)
    
    for i in xrange(len(ds_string_list)):
        if ds_string_list[i] not in permissable:
            if silent and isinstance(silent, str):
                ds_string_list[i] = silent
            elif silent:
                ds_string_list[i] = '_'
            else: 
                raise ValueError(SS_ERROR % (st, repr(ds_string[i])))
            
    return "".join(ds_string_list)    
    

def ss_from_ds(ds_string, silent=False):
    """
    A simple string is a string whose content bytes
    must be in a limited set of bytes.
    
    simple_strings can contain:
        A-Z, a-z, 0-9, safe specials.
        
    """
    ss_permissable = [chr(x) for x in SS_PERMISSABLE]
    return _from(ds_string, silent, ss_permissable, "Simple")
    

def cs_from_ds(ds_string, silent=False):
    """
    A complex string can have all the characters of a
    simple string + '[]/\|_-' this is pretty rigerous
    """
    cs_permissable = _get_permissable(CS_PERMISSABLE)
    return _from(ds_string, silent, cs_permissable, "Complex")

#def em_from_ds(ds_string):
    # After research this needs some serious work.
    #"""
    #An email string, can have any character legal in an
    #email address. So, lowers, uppers, 0-9 and .'s
    #"""
    #em_permissable = _get_permissable(EM_PERMISSABLE)
    #return _from(ds_string, False, em_permissable, "Email")
        
        
        
        
    
        
        
        
    
    

