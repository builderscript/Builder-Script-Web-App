# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import PickleType
from sqlalchemy.orm import relationship

from apps import db, login_manager
from apps.authentication.util import hash_pass


class Mailing(db.Model, UserMixin):

    __tablename__ = 'Mailing'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    joined = db.Column(db.String(64))


class CookieUsers(db.Model, UserMixin):

    __tablename__ = 'CookieUsers'

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.LargeBinary)
    # This will act like a List of Calculations objects attached to each User.
    # The "user" refers to the user property in the Calculations class.
    calculations = relationship("Calculations", back_populates="user")


class Calculations(db.Model, UserMixin):

    __tablename__ = 'Calculations'

    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of CookieUsers.
    user_id = db.Column(db.Integer, db.ForeignKey("CookieUsers.id"))
    # Create reference to the CookieUser object, the "calculations" refers to the calculations property in the CookieUser class.
    user = relationship("CookieUsers", back_populates="calculations")
    module_name = db.Column(db.String(64))
    slot = db.Column(db.Integer)
    description = db.Column(db.String(64))
    # Create property that enables to save json data and modify it by a key
    entry_data = db.Column(PickleType)
    result = db.Column(PickleType)
    datetime = db.Column(db.String(64))


class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
