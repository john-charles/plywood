from response import ResponseRedirect
from exceptions import Server403Exception


def view(auth_method=None):    

    class View:
        
        is_view = True
        
        def __init__(self,viewmethod):
            self.viewmethod = viewmethod
            if auth_method == None:
                self.is_allowed = lambda x: False
            else:
                self.is_allowed = auth_method
                        
        def __call__(self, request, **kwargs):
            if not self.is_allowed(request):
                raise Server403Exception("Forbidden",request.getPathInfo())
            else:
                return self.viewmethod( request, **kwargs )
                
    return View
            
            
            
        
        
    
        