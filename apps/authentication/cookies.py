from flask import request, make_response
from apps.authentication.models import CookieUsers, Calculations
from functools import wraps
from apps import db
import random
import hashlib
import binascii
import os
import json


def cookie_service(page):
    @wraps(page)
    def wrapper_function(*args, **kws):
        value = request.cookies.get('value')
        # if value exists
        if value:
            return page(*args, **kws)

        # if value does not exist
        else:
            # hash pin and save to db along with id
            pin = str(random.randint(1000000, 9999999))
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
            pin_hash = hashlib.pbkdf2_hmac('sha512', pin.encode('utf-8'), salt, 100000)
            pin_hash = binascii.hexlify(pin_hash)
            password = salt+pin_hash
            db.session.add(CookieUsers(password=password))
            db.session.commit()
            # set cookie on device
            resp = page(*args, **kws)
            resp = make_response(resp)
            max_age = 365 * 240 * 3600
            new_user = CookieUsers.query.filter_by(password=password).first()
            user_id = str(new_user.id)
            pin = str(pin)
            value = user_id + pin
            resp.set_cookie('value', value, max_age=max_age)
            return resp
    return wrapper_function


def cookies_get_user():
    value = request.cookies.get('value')
    if value:
        user_id = value[0]
        user_pin = value[1::]
        user_data = CookieUsers.query.filter_by(id=int(user_id)).first()
        user_salt = user_data.password[0:64]
        pin_hash = hashlib.pbkdf2_hmac('sha512', user_pin.encode('utf-8'), user_salt, 100000)
        pin_hash = binascii.hexlify(pin_hash)
        user_password = user_salt + pin_hash
        if user_password == user_data.password:
            return user_id
    else:
        return None


def cookies_get_data(user_id, module_name, slot):
    data = Calculations.query.filter_by(user_id=user_id, module_name=module_name, slot=slot).first()
    if data:
        description = data.description
        entry_data = json.loads(data.entry_data)
        result = json.loads(data.result)
        datetime = data.datetime
        return description, entry_data, result, datetime


def cookies_get_all_data(user_id, module_name):
    all_data = Calculations.query.filter_by(user_id=user_id, module_name=module_name).all()
    return all_data


def save_calculations(user_id, module_name, description, entry_data, result, slot, datetime):
    data = Calculations.query.filter_by(user_id=user_id, module_name=module_name, slot=slot).first()
    entry_data_json = json.dumps(entry_data)
    result_json = json.dumps(result)
    if data:
        data.description = description
        data.entry_data = entry_data_json
        data.result = result_json
        data.datetime = datetime
        db.session.commit()
    else:
        db.session.add(Calculations(user_id=user_id, module_name=module_name, slot=slot, description=description,
                                entry_data=entry_data_json, result=result_json, datetime=datetime))
        db.session.commit()


def check_slot(user_id, module_name):
    data = Calculations.query.filter_by(user_id=user_id, module_name=module_name).all()
    if data:
        next_slot = len(data) + 1
        return next_slot
    else:
        return 1
