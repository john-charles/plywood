
class Event:
    
    def __init__(self):
        self.call_list = list()
        
    def __iadd__(self, call):
        if not callable(call):
            raise ValueError("Object not callable!")
        self.call_list.append(call)
        return self
        
    def __call__(self, *args, **kw):
        for call in self.call_list:
            call(*args, **kw)