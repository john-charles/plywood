"""
Usage:
    
    class LoginFrom(Form):
        
        __meta__ = {'template_name':'login.html'}
        
        username = TextField()
        password = TextField(widget=widgets.PasswordWidget())
        
        def __call__(self):
            
            if self.is_valid:
                
                process(self.username.text, self.password.text)
                
            else:
            
                handle_errors()
                
            return self.response
    
        

"""
from plywood.http import Request
from fields import Field

class FormMeta(type):
    
    class Meta:
        pass
    
    def __new__(cls, name, bases, dct):
        
        class_name = name
        
        for name in dct.keys():
            if isinstance(dct[name], Field):
                dct[name].name = name
                
        return type.__new__(cls, name, bases, dct)

class Form:
    
    __meta__ = {}
    __metaclass__ = FormMeta
    
    __has_error = 0
    
    @property
    def is_valid(self):
        return self.__has_error == 0
    
    def __init__(self, post_data={}):
        self.__is_valid = 0
        
        if isinstance(post_data, Request):
            self.__request = post_data
            self.request = property(self.__p_request)
            
        elif isinstance(post_data, dict):
            self.validate(post_data)
        
    def validate(self, post_data):
        
        def validate(name, field):
            
            try:
                field.validate(post_data.get(name, None))
            except ValueError:
                self.__has_error += 1
        
        for field_name in dir(self):
            
            attr = getattr(self, field_name)            
            if isinstance(attr, Field):
                validate(field_name, attr)                    
        
        
    def __getitem__(self, name):
        if hasattr(self, name):
            attr = getattr(self, name)
            if isinstance(attr, Field):
                return attr.value
    
        raise KeyError("'%s' does not exist or is not a FormField" % name)
    
    def __setitem__(self, name, value):
        if hasattr(self, name):
            attr = getattr(self, name)
            if isinstance(attr, Field):
                attr.value = value
                return
        
        raise KeyError("'%s' does not exist or is not a FormField" % name)
            
        
        
    def __str__(self):
        
        text = str()
        
        for field_name in dir(self):
            attr = getattr(self, field_name)
            if isinstance(attr, BaseField):
                errors = attr.errors()
                if errors:
                    text = text + "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                        attr.get_label(), attr.render(), errors)
                else:
                    text = text + "<tr><td>%s</td><td>%s</td></tr>" % (
                        attr.get_label(), attr.render())
                    
        return text
                

        
                
                
                