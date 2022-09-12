from __future__ import print_function
from datetime import datetime
from apps.services import blueprint
from flask import render_template, request, redirect, url_for
from apps.services.sendinblue import api_send_msg, check_msg_status, api_add_contact
from apps.authentication.cookies import cookies_get_data, cookies_get_user, delete_calculations, cookies_get_all_data, \
    change_slot


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
        return redirect(url_for(f"calculations_blueprint.{route}", slot=next_slot))
    return render_template("home/page-403.html"), 403


# Delete calculation and set slot free
@blueprint.route('/delete-slot/<function_name>/<module_name>/<slot>', methods=['GET', 'POST'])
def delete_slot(slot, module_name, function_name):
    # Delete data from requested slot
    if request.method == "POST":
        user_id = cookies_get_user()
        data = cookies_get_data(user_id, module_name, slot)
        delete_calculations(user_id=user_id, module_name=module_name, slot=slot)
        # Sort the rest of the data so that there are no gaps between them. The rest of code is based on the slot order.
        user_data = cookies_get_all_data(user_id=user_id, module_name=module_name)
        if user_data:
            for data in user_data:
                if data.slot > int(slot):
                    change_slot(data)
        # Get back to previous existing slot
        if slot == "1":
            previous_slot = "1"
        else:
            previous_slot = str(int(slot) - 1)
        return redirect(url_for(f"calculations_blueprint.{function_name}", slot=previous_slot))
    return render_template("home/page-403.html"), 403
