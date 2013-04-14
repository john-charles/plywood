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

class Widget:
    
    def render(self, form, name, value):
        return "<!-- BaseWidget: name=%s -->" % name
    
class TextWidget(Widget):
    
    def render(self, form, name, value):
        id = "%s_%s" % (form, name)
        return """<input id="%s" type="text" name="%s" value="%s">""" % (id, name, value)
    
class PasswordWidget(Widget):
    
    def render(self, form, name, value):
        id = "%s_%s" % (form, name)
        if not value: value = ""
        return """<input id="%s" type="password" name="%s" value="%s">""" % (id, name, value)
    
class HiddenWidget(Widget):
    
    def render(self, form, name, value):
        id = "%s_%s" % (form, name)
        return """<input id="%s" type="hidden" name="%s" value="%s">""" % (id, name, value)
    
class TextareaWidget(Widget):
    
    def render(self, form, name, value):
        id = "%s_%s" % (form, name)
        if not value:
            value = ""
        return """<textarea id="%s" name="%s">%s</textarea>""" % (id, name, value)
    
class SelectDateWidget(Widget):
    
    date_min = None
    date_max = None
    
    def render(self, form, name, value):
        
        w = list()
        w.append('<select name="%s">')