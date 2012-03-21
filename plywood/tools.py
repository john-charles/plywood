import re
from imputil import import_entity

def url( pattern, call, **kwargs ):   
    if isinstance( call, str ):
        call = import_entity(call)
    
    if not callable(call):
        if not isinstance( call, tuple ):
            raise TypeError("A function, or callable class is required!")
    
    return ( re.compile( pattern ), call, kwargs )
    
def include( urllist_name ):
    if isinstance( urllist_name, str ):
        return import_entity(urllist_name + ".urllist")
    elif isinstance( urllist_name, tuple ):
        return urllist_name
    else:
        raise TypeError("A tuple is expected!")
    
def Urllist( *urllist ):    
    return include( tuple(urllist) )
    
def public( request ):
    return True