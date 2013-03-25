
def import_entity( name ):
    """
    This is an object agnostic importer which will import 
    any thing accessable on the python tree independent of 
    its type!
    """
    
    module = '.'.join(name.split('.')[:-1])
    method = name.split('.')[-1]
    
    m = __import__( module )
    
    if hasattr(m, method):
        return getattr(m, method)
    