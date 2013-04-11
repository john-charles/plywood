import traceback, sys

def import_entity(name):
    
    # This is one of the most frustrating pieces of code to write...
    path = None
    
    for part in name.split("."):
        if not path: path = part
        else: path = ".".join((path, part))
        try:
            #print "importing path: ", path
            #print "importing part: ", part
            m = __import__(path)
        except ImportError, e:
            missing_name = e.message.split(" ")[-1]
            #print "ImportError ocurred... missing_name = %s, part = %s" % (missing_name, part)
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


