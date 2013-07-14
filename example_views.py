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
import shutil
from plywood.views import View
from plywood.forms import Form
from plywood.forms.fields import *
from plywood.http import PageResponse

PAGE = '''
<html>
    <body>
        <h1>Plywood Test Web Application</h1>
        %(body)s
    </body>
</html>
'''

class Home(View):
    
    """
    Views are classes that extend the 'plywood.views.View' type.
    To make a view implement the __call__ method. All arguments
    in the url, eg matched regex patterns and the optional dicts
    will be passed into __call__ as keyword arguments.
    """   
    def __call__(self):
        # Demonstrates the session Wrapper functionality.
        # SessionWrappers are standard and implement the
        # 'abstract' (python has very limited tools for abstraction
        # so by abstract I mean that those methods are implemented as
        # 'pass' until the class is extended.) Session class. They
        # have many of the same features of the dict type but do not
        # inherit dict.
        if 'you_views' in self.request.session:
            you_views = self.request.session['you_views']
        else:
            you_views = 0
        self.request.session['you_views'] = you_views + 1
        
        # Demonstrates using the query sting passed in the url
        # to retrieve a value.
        special = self.request.query.get('special','Not Entered')
        
        page = '''You've viewed this page %s times!<br>
        <a href="/upload/">Upload a file!</a><br>
        <a href="/username/">Setup up username</a><br>
        Special value is &quot;%s&quot;''' % (you_views, special)
        
        # The last thing to do in any view is to return a 
        # Response object. For this example we will use a simple
        # PageResponse but there are also JsonResponse, 
        # RedirectResponse, LinkResponse (an abstraction of
        # RedirectResponse), and a few others to use.
        return PageResponse(self.request, PAGE % {'body':page})
    
class Upload(View):
    """An example of using a form to upload a file."""
    def __call__(self):
        
        # all request objects have a boolean property is_post
        # this property will return true when the request is 
        # a form submission.
        if self.request.is_post:
            my_file = self.request.post['my_file']
            ds_file = open("file.dat",'wb')
            shutil.copyfileobj(my_file[0], ds_file)
            ds_file.close()
            
        page = '''
        <form method="post" action="/upload/" enctype="multipart/form-data">
            <input type="hidden" value="%s" name="csrf_token">
            <input type="file" name="my_file">
            <input type="submit" value="Upload">
        </form>
        <img src="/_/file.dat">
        <a href="/">Back</a>
        ''' % self.request.csrf_token
        
        return PageResponse(self.request, PAGE % {'body':page})
    
class Username(Form):
    
    userage  = IntegerField()
    username = StringField()
    usermail = StringField()
    
    def init(self):
        """
        the 'init' method is called by the constructor and
        let's us set up our event handlers.
        """
        self.on_load += self.load_values 
        self.on_valid += self.store_values
        self.userage.on_change += self.userage_changed
        
    def load_values(self, username=None):
        """
        A example of an event handler. This event
        is called whenever the page is requested
        via a get, but not via a post.
        
        Here we set up some default values.
        NOTE: the keywords passed in to this
        method are the ones from the __call__
        method implemented in forms.Form.
        """
        self.userage.value = 55
        self.username.value = "Johnson"
        self.usermail.value = "Johnson@johnson.com"
        
    def store_values(self):
        """
        Handles the even that the from is valid.
        Here we would save our values to the 
        database or whatever.
        
        In this example we just print them.
        If we want to clear the form state now
        is a good time to do it.
        """
        print self.userage.value
        print self.username.value
        print self.usermail.value
        
    def userage_changed(self):
        """
        a trivial example of a value.on_change
        event handler.
        """
        print "userage_changed called"
        self.userage.value = self.userage.value + 100
        
    def render(self):
        
        page = """
        <form method="POST" action="/username/">
            %(csrf_token)s
            %(userage)s  %(userage_error)s
            %(username)s %(username_error)s
            %(usermail)s %(usermail_error)s
            <input type="submit" name="Update">
        </form>
        <a href="/">Back</a>
        """
        
        context = {}
        context["csrf_token"] = self.request.csrf_token_field
        context['userage'] = self.userage
        context['userage_error'] = self.userage.error
        context['username'] = self.username
        context['username_error'] = self.username.error
        context['usermail'] = self.usermail
        context['usermail_error'] = self.usermail.error
        
        page = PAGE % {'body': page % context}
        return PageResponse(self.request, page)
    
    

        
        
    
    
    
        
        