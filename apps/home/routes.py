# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from __future__ import print_function
from apps.home import blueprint
from flask import render_template
from datetime import datetime
from jinja2 import TemplateNotFound
from apps.authentication.cookies import cookie_service

# Configure copyright year to update
year = datetime.now().year


# Basic routes # Basic routes # Basic routes # Basic routes # Basic routes # Basic routes # Basic routes # Basic routes

@blueprint.route('/')
def home_page():
    return render_template('home/index.html', year=year)


@blueprint.route('/kalkulatory')
@cookie_service
def calculator_page():
    return render_template('calculator/kalkulatory.html', id='kalkulatory')


@blueprint.route('/kalkulatory/informacje')
@cookie_service
def information_page():
    return render_template('calculator/informacje.html', id='informacje')


# Last call - if requested url not found # Last call - if requested url not found # Last call - if requested url not found

@blueprint.route('/<template>')
def route_template(template):
    try:
        return render_template(template)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
