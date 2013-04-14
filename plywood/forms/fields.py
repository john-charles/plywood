"""
This file is part of plywood.
    
    Copyright 2013 John-Charles D. Sokolow - <john.charles.sokolow@gmail.com>

    plywood is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    plywood is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with plywood.  If not, see <http://www.gnu.org/licenses/>.
    
Please see README for usage details.   
"""
__all__ = ['DateField','FloatField','IntegerField','StringField']
from plywood.kinds import *
from plywood.event import Event
from widgets import TextWidget
from datetime import date, datetime

class Field:
    
    default   = None
    error     = ''
    form_name = None
    name      = None
    multipart = False
    required  = True
    value     = None
    widget    = TextWidget()
    
    
    def __init__(self, default=None, widget=None, required=True):
        if widget: self.widget = widget
        if default: self.default = default
        if not required: self.required = False
        
        self.on_error = Event()
        self.on_change = Event()
        
    def validate(self, d_data):
        if not d_data and self.required:
            self.error = "This field is required!"
            raise ValueError()
    
    def __str__(self):
        d_value = self.value if self.value else ''
        if isinstance(d_value, basestring):
            hs_value = hs_from_ds(d_value)
        else:
            hs_value = str(d_value)
        return self.widget.render(self.form_name, self.name, hs_value)
    
class DateField(Field):
    
    def __init__(self, default=None, widget=None, required=True, date_min=None, date_max=None):
        Field.__init__(self, default, widget, required)
        self.date_min = self.widget.date_min = date_min
        self.date_max = self.widget.date_max = date_max
        
    def validate(self, data):
        Field.validate(self, data)
        
        drange = (self.date_min.strftime("%Y-%m-%d"),
                  self.date_max.strftime("%Y-%m-%d"))
        
        if isinstance(data, list):
            if len(data) != 3:
                self.error = "Need year month day, got something else!"
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
            raise Exception("Not Implemented")
            
            
            
    
class FloatField(Field):
    
    def __init__(self, default=0.0, widget=None, required=True):
        Field.__init__(self, default, widget, required)
        
    def validate(self, data):
        Field.validate(self, data)
        
        try: self.value = float(data)
        except ValueError, e:
            self.error = "A decimal number is required!"
            raise e
        
    
class IntegerField(Field):
    
    def __init__(self, default=0, widget=None, required=True):
        Field.__init__(self, default, widget, required)
        
    def validate(self, data):
        Field.validate(self, data)
        
        try: self.value = int(data)
        except ValueError, e:
                self.error = "A number is required"
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
        

    
        
    
    