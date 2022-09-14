from __future__ import print_function
from apps.admin import blueprint
from flask import render_template, redirect, url_for
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


@blueprint.route('/zarządzaj')
@admin_only
def admin_manage():
    users = Users.query.order_by(Users.time_left).all()
    now = datetime.now()
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

