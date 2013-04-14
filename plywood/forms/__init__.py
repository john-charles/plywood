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
            
How do I implement this.

1. Get:
- Request comes into a form.
- Call on_load, let the user load the
    data on the form.
    Should this only be called on "GET" requests?
- Save each form field to the session.
- Render the form.

2. Post:
- Request comes into a from. This is passing a request instead of a dict.
- Iterate over the fields.
    1. Validate the field.
    4. If the field failed to validate:
        - set the fields error appropriately.
        - fire the on_error event.
        - set the field value to the copy stored in the session.
        
- If the entire form is valid:
    - Check each field against the value saved in the session.
    - If the are different fire the on changed event.
    - fire the on_valid event (Do this now so that we have an oppertunity to do whatever in the various on_change events.)
- Save each form filed to the session.
- Render the form.

Django Style:
- Form is created with a dictionary of values.
- Do the 'Iterate over fields' part of the Post request above.
- except, if the field is invalid set it to the default.
- If the entire form is valid:
    - Set a flag 'is_valid'
    
    
        

"""
from fields import Field
from plywood.event import Event
from plywood.http import Request, LinkResponse


class FormMeta(type):
    
    class Meta:
        pass
    
    def __new__(cls, name, bases, dct):
        
        class_name = name
        
        for name in dct.keys():
            if isinstance(dct[name], Field):
                dct[name].name = name
                dct[name].form_name = class_name
                
        return type.__new__(cls, class_name, bases, dct)

class Form:

    __metaclass__ = FormMeta
    
    # If this is set to false values will
    # not be saved to the session and the
    # on_change event will never be fired.
    watch_changes = True
    __redirect = None
    
    def __call__(self, **kwargs):
        f_got_name = self.__sf_name("f_got")
        if self.request.is_get:
            self.on_load(**kwargs)
            self.session[f_got_name] = True
        
        if self.request.is_post:
            # This validates that on change
            # will be called. Even if the
            # from is submitted without a get.
            # That's an odd situation only 
            # in testing. NOTE: Maybe I should
            # take this out?
            if f_got_name not in self.session:
                self.on_load(**kwarg)
                
            if self.is_valid:
                if self.watch_changes:
                    self.__change()
                self.on_valid()
        
        # If were watching changes we always
        # save our fields, if it's a post or not!
        if self.watch_changes:
            self.__save_fields()
        
        self.__clear_events()
        if isinstance(self.__redirect, LinkResponse):
            return self.__redirect
        return self.render()
    
    def __change(self):
        """ 
        Check if the user submitted data is different
        than the session stored data and fire change 
        events on fields that have changed.
        """
        for name, field in self.__iter_fields():
            name = self.__sf_name(name)
            if name in self.session:
                if self.session[name] != field.value:
                    field.on_change()
            
                
                
    def __save_fields(self):
        """
        Save any data currently in the fields to
        the user's session so that it can be checked
        on the next post.
        """
        for name, field in self.__iter_fields():
            name = self.__sf_name(name)
            if not field.error:
                self.session[name] = field.value
        
    
    def __init__(self, req_or_dict=None):
        self.__c_errors = -1
        # We use -1 so that if the form is never
        # validated 'is_valid' will fail.
        
        if isinstance(req_or_dict, Request):
            self.__init_request(req_or_dict)
        elif isinstance(req_or_dict, dict):
            self.__init_dict(req_or_dict)
        elif req_or_dict:            
            types = (Request, dict, type(req_or_dict))
            raise ValueError("Expected %s or %s, got %s" % types)
        
    def __init_dict(self, post_data):
        self.__validate(post_data)
        
    def __init_request(self, request):
        self.request = request
        self.session = request.session
                
        # Set these up here, then call the public
        # 'init' method for the user to load the handlers.
        self.on_load = Event()
        self.on_valid = Event()
        self.init()
        
        if request.is_post:
            self.__validate(request.post)
            
    def __iter_fields(self):
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Field):
                yield name, attr                
    
    def __sf_name(self, key_name):
        form_name = self.__class__.__name__
        return "%s_storedvalue_%s" % (form_name, key_name)
        
    def __validate(self, post_data):
        c_errors = 0
        for name, attr in self.__iter_fields():
            try: attr.validate(post_data.get(name, None))
            except ValueError, e:
                attr.on_error(e)
                c_errors += 1
        
        # If no errors this will overwrite the -1 to validate
        # the form's data.
        self.__c_errors = c_errors
        
    def __clear_events(self):
        
        for name, field in self.__iter_fields():
            field.on_change.clear()
            field.on_error.clear()
        
    def clear_saved(self):
        """
        Let the user delete all fields saved in the
        session. This will prevent any on_change events
        from being fired.
        """
        for name, attr in self.__iter_fields():
            sf_name = self.__sf_name(name)
            if sf_name in self.session:
                del self.session[sf_name]
        
        
    def init(self):
        pass
                
    @property
    def is_valid(self):
        """If we have no errors then the form is valid."""
        return self.__c_errors == 0
    
    def redirect(self, url, query={}, fragment=None):
        self.__redirect = LinkResponse(self.request, url, query, fragment)
        
    
    def render(self):
        pass
                    
        
    
    