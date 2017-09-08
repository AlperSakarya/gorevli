#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, render_template, url_for, request
from forms import signupform, donationform, LoginForm, SmsForm
from squareconnect.rest import ApiException
from squareconnect.apis.customers_api import CustomersApi
from squareconnect.models.create_customer_request import CreateCustomerRequest
from squareconnect import Money
import uuid, json, unirest
import time
import re
import auth  # I pass my Square access token here and import this auth.py file
# squareconnect.configuration.access_token = 'put access token here'
from auth import client, auth_token, account_sid, location_id, from_number, access_token

api_instance = CustomersApi()
app = Flask(__name__)
app.secret_key = 'myverylongsecretkey'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/donate')
def donation():
    return render_template('donate.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/admin')
def admin_login_page():
    return render_template('admin.html')


def get_customers():

    try:
        # list customers
        for i in api_response.customers:
            print("Email Address: ")
            print(i.email_address)
            print("Phone Number: ")
            print(i.phone_number)
    except ApiException as e:
        print('Exception when calling CustomersApi->list_customers: %s\n' % e)


@app.route('/charge', methods=['POST'])
def charge_card():
    card_nonce=request.form['nonce']
    donation=int(request.form['donation-amount']) * 100
    response = unirest.post('https://connect.squareup.com/v2/locations/' + location_id + '/transactions',
  headers={
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + access_token,
  },
  params = json.dumps({
    'card_nonce': card_nonce,
    'amount_money': {
      'amount': donation,
      'currency': 'USD'
    },
    'idempotency_key': str(uuid.uuid1())
  })
)	
    return render_template('donate-response.html',result=response.body)


@app.route('/signuprequest', methods=['POST'])
def signuprequest():
    form = signupform()
    try:
        api_response = api_instance.create_customer(CreateCustomerRequest(
            given_name=form.memberName.data,
            email_address=form.notificationEmail.data,
            phone_number=form.phoneNumber.data

        ))
        return render_template('signup-response.html', exception="", isim=form.memberName.data,
                               email=form.notificationEmail.data, telefon=form.phoneNumber.data)

    except ApiException as e:
        return render_template('signup-response.html', exception=e.body)


@app.route('/adminlogin', methods=['POST'])
def admin_login():
    form = LoginForm()
    if form.adminEmail.data == auth.admin_Email and form.adminPassword.data == auth.admin_Password:
        api_response = api_instance.list_customers()
        return render_template('gorevli-paneli.html', api_response=api_response)

    else:
        return render_template('donate-response.html', exception="Yanlis Bilgi Girildi")


@app.route('/send-sms', methods=['POST'])
def send_sms_message():
    # List customers from Square and SMS with twilio
    # Setting from number for members

    form = SmsForm()
    sms_message = form.sms_content.data
    try:
        api_response = api_instance.list_customers()
        for i in api_response.customers:
            if type(i.phone_number) == str:
                member_number = re.sub("[^0-9]", "", i.phone_number)
                message = client.api.account.messages.create(to=member_number, from_=from_number, body=sms_message)
                time.sleep(3)
                return render_template('gorevli-paneli.html', api_response=api_response,
                                       success_message="SMS was sent to all members!")
    except ApiException as e:
        return render_template('gorevli-paneli.html', api_response=api_response, exception=e)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


