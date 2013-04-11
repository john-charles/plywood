from widgets import TextWidget
from datetime import date, datetime

class Field:
    
    default   = None
    error     = None
    name      = None
    multipart = False
    required  = True
    value     = None
    widget    = TextWidget()
    
    
    def __init__(self, default=None, widget=None, required=True):
        if widget: self.widget = widget
        if default: self.default = default
        if not required: self.required = False
        
    def validate(self, data):
        if not data and self.required:
            self.error = "This field is required!"
            raise ValueError()
    
    def __str__(self):        
        return self.widget.render(self.name, self.value)
    
class DateField(Field):
    
    def __init__(self, default=None, widget=None, required=True, date_min=None, date_max=None):
        Field.__init__(self, default, widget, required)
        self.date_min = date_min
        self.date_max = date_max
        
    def validate(self, data):
        Field.validate(self, data)
        
        drange = (self.date_min.strftime("%Y-%m-%d"),
                  self.date_max.strftime("%Y-%m-%d"))
        
        if isinstance(data, list):
            if len(data) != 3:
                self.error = "Hmmm, this is strange, bad date!"
                raise ValueError(self.error)
            
            year, month, day = data
            date = date(year=year, month=month, day=day)
            if self.date_max and date > self.date_max:
                self.error = "Date must be in range %s to %s" % drange
                raise ValueError(self.error)
            if self.date_min and date < self.date_max:
                self.error = "Date must be in range %s to %s" % drange
                raise ValueError(self.error)
            
            self.value = date
            
        else:
            
            pass
            
            
            
    
class FloatField(Field):
    
    def __init__(self, default=0.0, widget=None, required=True):
        Field.__init__(self, default, widget, required)
        
    def validate(self, data):
        Field.validate(self, data)
        
        try: self.value = float(data)
        except ValueError, e:
            self.error = "A decimal number is required!"
            raise e
    
    
class StringField(Field):
    
    def __init__(self, default=0, widget=None, required=True, max_length=0):
        Field.__init__(self, default, widget, required)
        self.max_length = max_length
        
    def validate(self, data):
        Field.validate(self, data)
        
        if self.max_length and len(data) > self.max_length:
            self.error = "The text cannot be longer than %s characters" % self.max_length
            raise ValueError(self.error)
        
        self.value = data
    
class IntegerField(Field):
    
    def __init__(self, default=0, widget=None, required=True):
        Field.__init__(default, widget, required)
        
    def validate(self, data):
        Field.validate(self, data)
        
        try: self.value = int(data)
        except ValueError, e:
                self.error = "A number is required"
                raise e
    
        
    
    