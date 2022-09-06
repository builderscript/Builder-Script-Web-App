from __future__ import print_function
from datetime import datetime
from apps.services import blueprint
from flask import render_template, request, redirect, url_for
from apps.services.sendinblue import api_send_msg, check_msg_status, api_add_contact


# Send message from home page
@blueprint.route('/message-status', methods=['GET', 'POST'])
def send_message():
    if request.method == "POST":
        send_smtp_email = api_send_msg()
        response = check_msg_status(send_smtp_email)
        return render_template("home/simple-response.html", response=response)
    else:
        return render_template("home/page-403.html"), 403


# Add to mailing list from home page
@blueprint.route('/add-to-mailing-list', methods=['GET', 'POST'])
def add_mail():
    if request.method == "POST":
        now = datetime.now()
        date_time_str = str(now.strftime("%Y-%m-%d %H:%M:%S"))
        data = request.form
        email = data["email"]
        response = api_add_contact(email, date_time_str)
        return render_template("home/simple-response.html", response=response)
    else:
        return render_template("home/page-403.html"), 403


# Add new calculation slot from requested module
@blueprint.route('/add-new-slot/<route>/<slot>/<next_slot>', methods=['GET', 'POST'])
def add_new_slot(next_slot, slot, route):
    if request.method == "POST":
        return redirect(url_for(f"home_blueprint.{route}", slot=next_slot))
    return render_template("home/page-403.html"), 403


# Delete calculation and set slot free
@blueprint.route('/delete-slot/<slot>')
def delete_slot(slot):
    print(slot)
    # Stop right here. Figure out how to delete data from db and reorder them 0++ not to make a gap between them.
    # So next_slot would still work perfectly fine
    # Start sorting number above deleted one to the first occur.
    return render_template("calculator/kalkulatory.html")
