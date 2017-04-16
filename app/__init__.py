#!/usr/bin/env python2
#! coding: utf-8
"""A fanfou bot to manage your TODO list"""

from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

import views
from .models import db
