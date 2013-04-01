
def import_entity(name):
    
    #print "importing: ", name
    # This is one of the most frustrating pieces of code to write...
    path = None
    
    for part in name.split("."):
        if not path: path = part
        else: path = ".".join((path, part))
        try:
            m = __import__(path)
        except ImportError:
            pass
    
    if name.count(".") == 0:
        return m
    
    else:
        tail = name.replace(name.split('.')[0] + ".","")
        for part in tail.split("."):

            if hasattr(m, part):
                m = getattr(m, part)
            else:
                raise ImportError("No object %s" % part)
        
        return m


