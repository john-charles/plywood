from forms import Form

class View:
    
    def __init__(self, request):
        self.__request = request
        
    @property
    def request(self):
        return self.__request
    
    def __call__(self, **kwargs):
        raise NotImplemented()
    
    
    
    