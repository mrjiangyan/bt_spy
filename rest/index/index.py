#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from jinja2 import TemplateNotFound
from flask import render_template,abort
import flask

blueprint = flask.Blueprint(
    'index',
    __name__,
    url_prefix='/',
    template_folder="templates",
    static_folder='static'
)

# @blueprint.route('/favicon.ico')
# def index():
#     try:
#         return render_template('favicon.ico')
#     except TemplateNotFound:
#         print('2222')
#         abort(404)
        

@blueprint.route('/')
def index():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        print('111111')
        abort(404)


