# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from __future__ import print_function
from apps.home import blueprint
from flask import render_template, request
from datetime import datetime
from jinja2 import TemplateNotFound
from apps.authentication.cookies import cookie_service, cookies_get_user, save_calculations, cookies_get_data, \
    check_slot, cookies_get_all_data

# General rules # General rules # General rules # General rules # General rules # General rules # General rules
MAX_SLOT = 9  # every use can have maximum 0-9 - 10 slots

# Calculations routes # Calculations routes # Calculations routes # Calculations routes # Calculations routes
CONCRETE = 'moduł-żelbetowy'

# Configure copyright year to update / configure datetime of calculations
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


@blueprint.route(f'/kalkulatory/{CONCRETE}/dodawanie/<int:slot>', methods=['GET', 'POST'])
@cookie_service
def dodawanie_page(slot):
    # name the module first
    module_name = "dodawanie"
    # set the route to create another calculations slots
    route = "dodawanie_page"
    # get cookie user data
    user_id = cookies_get_user()
    # get name of the blueprint function
    function_name = dodawanie_page.__name__
    # get data, carry out calculations and save to db
    if request.method == "POST":
        calc_data = request.form
        first_number = float(calc_data["liczba1"])
        second_number = float(calc_data["liczba2"])
        message = str(calc_data["tekst"])
        final_number = first_number + second_number
        entry_data = {"liczba1": first_number, "liczba2": second_number}
        result = {"wynik": final_number}
        now = datetime.now()
        date_time_str = str(now.strftime("%Y-%m-%d %H:%M:%S"))
        if user_id:
            save_calculations(user_id=user_id, module_name=module_name, description=message, entry_data=entry_data,
                              result=result, slot=slot, datetime=date_time_str)
    # return data into page filling requested slot page
    data = cookies_get_data(user_id, module_name, slot)
    # return data into archive to enable route to another slots
    all_data = cookies_get_all_data(user_id, module_name)
    # check if user have more space for calculations
    next_slot = check_slot(user_id=user_id, module_name=module_name)
    if 0 < slot <= next_slot:
        return render_template('calculator/dodawanie.html', data=data, slot=slot, next_slot=next_slot, route=route,
                               all_data=all_data, max_slot=MAX_SLOT, module_name=module_name, function_name=function_name)
    else:
        return render_template('home/page-404.html')


# Last call - if requested url not found # Last call - if requested url not found # Last call - if requested url not found

@blueprint.route('/<template>')
def route_template(template):
    try:
        return render_template(template)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
