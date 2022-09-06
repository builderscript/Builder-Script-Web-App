from apps.authentication.models import Mailing
from sib_api_v3_sdk.rest import ApiException
from flask import request
from pprint import pprint
from apps import db
import sib_api_v3_sdk
from key_config import SENDINBLUE_API_KEY, SENDINBLUE_TO, SENDINBLUE_SENDER, SENDINBLUE_NAME


# Configure e-mail sender API
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = SENDINBLUE_API_KEY
api_instance_send_email = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
api_instance_add_contact = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))


# Send message using api
def api_send_msg():
    message_data = request.form
    name = message_data["name"]
    email = message_data["email"]
    message = message_data["message"]
    with open('apps/templates/sendinblue/send_message.html', encoding='utf-8') as html:
        message_text = html.read()
        message_text = message_text.replace('name_goes_here', name)
        message_text = message_text.replace('email_goes_here', email)
        message_text = message_text.replace('message_goes_here', message)
    subject = "Otrzymałeś wiadomość z Builder Script"
    html_content = message_text
    sender = {"name": "BuilderScript", "email": SENDINBLUE_SENDER}
    to = [{"email": SENDINBLUE_TO, "name": SENDINBLUE_NAME}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content,
                                                   subject=subject, sender=sender)
    return send_smtp_email


# Check if sent or catch exception
def check_msg_status(send_smtp_email):
    try:
        api_response = api_instance_send_email.send_transac_email(send_smtp_email)
        pprint(api_response)
        response = "Wiadomość została pomyślnie wysłana."
        return response
    except ApiException as e:
        pprint("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        response = "Ups... Coś poszło nie tak."
        return response


# Add new contact to api and db
def api_add_contact(email, date_time_str):
    search_email = Mailing.query.filter_by(email=email).first()
    if search_email:
        response = "Adres e-mail został już wcześniej dodany."
        return response
    else:
        time = str(date_time_str)
        new_email = Mailing(email=email, joined=time)
        db.session.add(new_email)
        db.session.commit()
        create_contact = sib_api_v3_sdk.CreateContact(email=email, list_ids=[2])
        try:
            api_response = api_instance_add_contact.create_contact(create_contact)
            pprint(api_response)
            response = "Adres e-mail został pomyślnie dodany."
            return response
        except ApiException as e:
            pprint("Exception when calling ContactsApi->create_contact: %s\n" % e)
            response = "Ups... Coś poszło nie tak."
            return response
