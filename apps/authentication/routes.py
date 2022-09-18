# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass
from datetime import datetime, timedelta
from apps.authentication.secure import is_safe_url
import random


# Configure copyright year to update
year = datetime.now().year


# Login & Registration


@blueprint.route('/logowanie', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            next = request.args.get('next')
            if not is_safe_url(next):
                return render_template('home/page-403.html'), 403
            else:
                return redirect(url_for('home_blueprint.calculator_page'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Nieprawidłowa nazwa użytkownika lub hasło',
                               form=login_form, year=year)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form, year=year)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/rejestracja', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Nazwa użytkownika zajęta!',
                                   success=False,
                                   form=create_account_form, year=year)

        # else we can create the user
        now = datetime.now()
        users = Users.query.all()
        if not users:
            time = now + timedelta(days=365000)
        else:
            time = now + timedelta(days=35)
        avatar = str(random.randint(1, 5))
        user = Users(**request.form, register_date=now, time_left=time, avatar=avatar, active=True)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='Konto zostało utworzone!',
                               success=True,
                               form=create_account_form, year=year)

    else:
        return render_template('accounts/register.html', form=create_account_form, year=year)


@blueprint.route('/wyloguj')
def logout():
    logout_user()
    return redirect(url_for('home_blueprint.home_page'))


# Errors


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
