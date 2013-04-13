#! /usr/bin/env python

from plywood.urls import Urls, url
from plywood.wsgi import WSGIHandler
from plywood.utils import dev_server
from plywood.wrappers import WList, wconfig

OPTIONS = {"secret_key":"THis is a test secret_key", 'print_exceptions':True}

URLS = Urls(
    
    url(r'^$','test_views.Home'),
    url(r'^upload/$','test_views.Upload'),
)

WRAPPERS = WList(
    wconfig("plywood.wrappers.CookieSessionWrapper"),
    
)

if __name__ == "__main__":
    
    application = WSGIHandler(URLS, WRAPPERS, OPTIONS)
    dev_server(application, bindport=8052)
    
    
    