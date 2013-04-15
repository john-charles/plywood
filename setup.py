#!/usr/bin/env python
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
execfile("plywood/version.py")

from distutils.core import setup

setup(
    name='Plywood',
    version=__version__,
    description='A lightweight WSGI Web Framework',
    long_description='''Plywood is a WSGI Web Framework
    built to be database and template agnostic.''',
    author='John-Charles D. Sokolow',
    author_email='john.charles.sokolow@gmail.com',
    url='',
    packages=['plywood', 'plywood.forms'],
    license='GNU Lesser General Public License', 
)
