#! /usr/bin/env python
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
from plywood.urls import Urls, url
from plywood.wsgi import WSGIHandler
from plywood.utils import dev_server
from plywood.wrappers import WList, wconfig

# Configure global options. This dictionary will be globally available
# to all Wrapper instances View instances and Request instances.
# note elements that take their own options are merged and override this
# dictionary. This is useful if you want to set a global default and
# and override that default for one specific element.
OPTIONS = {
    "secret_key": """This is an example secret key. 
You should change this to something more secure in your application."""}
# NOTE: A secret_key must be set here, if not plywood will fail to load.

# URLS are similar to django. They start with a pattern to be matched
# followed by either a string argument which holds the path to a class
# that extends View or Form, or a callable function.
# A third argument option can be specified which will be passed into
# the view as a keyword argument.
URLS = Urls(
    
    url(r'^$','example_views.Home'),
    url(r'^upload/$','example_views.Upload'),
    url(r'^username/$','example_views.Username'),
)

# Wrappers are simplar to django middleware. They extend
# the framework but adding the ability to modify both 
# requests and responses. The 'wconfig' function takes
# an instatiated wrapper, or a string with the name of
# the wrapper. The second argument is an optional 
# dictionary of overrides or local options needed for
# the specific wrapper.
WRAPPERS = WList(
    wconfig("plywood.wrappers.CookieSessionWrapper"),
    
)

# Let's create our application instance. This application
# is what handles the wsgi requests. And it can be deployed
# to anything that supports wsgi. Including wsgi, mod_wsgi
# fastcgi, fcgi, and even cgi!
application = WSGIHandler(URLS, WRAPPERS, OPTIONS)

if __name__ == "__main__":
    
    # Deployment of your WSGIHandler will be server specific
    # but for the example herin we simply use the builtin
    # wsgi server which comes with plywood. The 'dev_server'
    # will serve your application on local host, and has 
    # some convienient features, including the ability to
    # automatically reload your application when any of 
    # your source files change. This is handy!    
    dev_server(application, bindport=8052)
    
    
    