from __future__ import print_function
from apps.admin import blueprint
from flask import render_template, redirect, url_for, request
from apps.authentication.secure import admin_only
from apps.authentication.models import Users
from datetime import datetime, timedelta
from apps import db


@blueprint.route('/panel_administratora')
@admin_only
def admin_tools():
    return render_template('admin/index-admin.html', id='admin_tools')


@blueprint.route('/statystyki')
@admin_only
def admin_stats():
    return render_template('admin/admin-tools.html', id='stats')

@blueprint.route('/dodaj_użytkownika')
@admin_only
def admin_add_user():
    return render_template('admin/admin-add-user.html', id='add')


@blueprint.route('/zarządzaj')
@admin_only
def admin_manage():
    now = datetime.now()
    page = request.args.get('page', 1, type=int)
    users = Users.query.order_by(Users.time_left).paginate(page=page, per_page=50)
    return render_template('admin/manage.html', id='manage', users=users, datetime=now)


@blueprint.route('/delete_user/<id>/<pin>/<username>')
@admin_only
def delete_user(id, pin, username):
    data = Users.query.filter_by(id=id, pin=pin, username=username).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('admin_blueprint.admin_manage'))


@blueprint.route('/extend_user/<id>/<pin>/<username>')
@admin_only
def extend_user(id, pin, username):
    user = Users.query.filter_by(id=id, pin=pin, username=username).first()
    user.time_left += timedelta(days=35)
    db.session.commit()
    return redirect(url_for('admin_blueprint.admin_manage'))


# TEST # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST  # TEST
@blueprint.route('/test_only')
@admin_only
def add_k_users():
    import random
    for index in range(0, 205):
        now = datetime.now()
        seconds = random.randint(1, 60*60)
        time = now + timedelta(seconds=seconds)
        pin = '76' + str(index)
        username = "BuilderScriptUser#" + str(index)
        password = "BuilderScriptUser#" + str(index)
        avatar = str(random.randint(1, 5))
        db.session.add(Users(pin=pin, username=username, password=password, register_date=now, time_left=time, avatar=avatar, active=True))
        db.session.commit()
    return redirect(url_for('admin_blueprint.admin_add_user'))
