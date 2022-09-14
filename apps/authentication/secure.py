from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect
from functools import wraps
from flask_login import current_user
from flask import render_template


# Securely Redirect Back
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


# Administrator only without freely link access
def admin_only(page):
    @wraps(page)
    def wrapper_function(*args, **kws):
        if current_user.id != 1:
            return render_template('home/page-403.html'), 403
        return page(*args, **kws)
    return wrapper_function
