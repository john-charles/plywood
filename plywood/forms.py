import _widgets as widgets

class BaseField:
    
    _label = None
    _errors = None
    
    def setName(self, name):
        self.__name = name
        
    def _getName(self):
        return self.__name
    
    def get_label(self):
        if self._label:
            return self._label
        else:
            return self._getName()
    
    # Validates data returns True if data validated successfully.
    def validate(self, data):
        raise TypeError("BaseField")
    
    # Retrieves previously validated data.
    def cleaned_data(self):
        return None
        
    def render(self):
        return self.widget.render(self._getName(), self.cleaned_data())
    
    def errors(self):
        if self._errors:
            if hasattr(self, "_errors_str"):
                return self._errors_str
            else:
                return "This field is required"
        else:
            return ""
    
    
class IntegerField(BaseField):
    
    def __init__(self, default=0, label=None, widget=widgets.TextWidget()):
        self._label = label
        self.value = default
        self.widget = widget
        
    def validate(self, data):
        try:
            self.value = int(data)
        except TypeError, e:
            self._errors = True
            raise e
        
    def cleaned_data(self):
        return self.value
    
    
class TextField(BaseField):
    
    def __init__(self, label=None, default=None, max_length=None, widget=widgets.TextWidget()):
        self._label = label
        self.widget = widget
        if default:
            self.value = default
        else:
            self.value = str()
        self.max_length = max_length
        
    def validate(self, data):
        if self.max_length:
            if len(data) >= self.max_length:
                self._errors = True
                self._errors_str = "This field can not be longer than %s" % self.max_length
                raise AssertionError("Too long")
            
        self.value = data
        
    def cleaned_data(self):
        return self.value
        

class _FormMeta(type):
    
    def __new__(cls, name, bases, dct):
        for name in dct.keys():
            if isinstance(dct[name], BaseField):
                dct[name].setName(name)
        
        return type.__new__(cls, name, bases, dct)
            

class Form:
    
    __metaclass__ = _FormMeta
    
    cleaned_data = None
    
    def __init__(self, post_data={}):
        self.post_data = post_data
        
    def __getitem__(self, name):
        if self.cleaned_data:
            return self.cleaned_data[name]
        else:
            raise KeyError("form is not valid")
        
    def is_valid(self):
        
        self.cleaned_data = dict()
        
        for field_name in dir(self):
            
            attr = getattr(self, field_name)
            
            if isinstance(attr, BaseField):
                try:
                    attr.validate(self.post_data.get(field_name, None))
                    self.cleaned_data[field_name] = attr.cleaned_data()
                except:
                    return False
                    
        return True
        
    def table(self):
        
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
                
        
        
                
                
                