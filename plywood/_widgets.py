
class Widget:
    
    def render(self, name, value):
        return "<!-- BaseWidget: name=%s, value=%s -->" % (name, value)
    
class TextWidget(Widget):
    
    def render(self, name, value):
        return """<input id="%s" type="text" name="%s" value="%s">""" % (name, name, value)
    
class TextareaWidget(Widget):
    
    def render(self, name, value):
        if not value:
            value = ""
        return """<textarea id="%s" name="%s">%s</textarea>""" % (name, name, value)