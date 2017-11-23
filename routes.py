#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, render_template, url_for, request
from forms import signupform, donationform, LoginForm, SmsForm
from squareconnect.rest import ApiException
from squareconnect.apis.customers_api import CustomersApi
from squareconnect.models.create_customer_request import CreateCustomerRequest
import uuid, json, unirest, re, time
import auth  # I pass my Square access token here and import this auth.py file
import stripe
from auth import client, auth_token, account_sid, location_id, from_number, access_token, STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY


api_instance = CustomersApi()
app = Flask(__name__)
app.secret_key = 'myverylongsecretkey'
stripe_keys = {'secret_key': STRIPE_SECRET_KEY, 'publishable_key': STRIPE_PUBLISHABLE_KEY}
stripe.api_key = stripe_keys['secret_key']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/donate')
def donation():
    return render_template('donate.html', key=stripe_keys['publishable_key'])


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/admin')
def admin_login_page():
    return render_template('admin.html')


@app.route('/signuprequest', methods=['POST'])
def signuprequest():
    form = signupform()
    try:
        if form.notificationEmail.data != "":
            api_response = api_instance.create_customer(CreateCustomerRequest(
                given_name=form.memberName.data,
                email_address=form.notificationEmail.data,
                phone_number=form.phoneNumber.data

            ))
        else:
            api_response = api_instance.create_customer(CreateCustomerRequest(
                given_name=form.memberName.data,
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
        try:
            api_response = api_instance.list_customers()
            return render_template('gorevli-paneli.html', api_response=api_response, registered_members=len(api_response.customers))

        except ApiException as e:
            return render_template('login-response.html', exception_message="Hata olustu", e=e)

    else:
        return render_template('login-response.html', exception_message="Yanlis Bilgi Girildi")


@app.route('/send-sms', methods=['POST'])
def send_sms_message():
    # List customers from Square and SMS with twilio
    # Setting from number for members
    form = SmsForm()
    sms_message = form.sms_content.data
    registered_members = 0

    try:
        api_response = api_instance.list_customers()
        for i in api_response.customers:
            if type(i.phone_number) == str:
                member_number = re.sub("[^0-9]", "", i.phone_number)
                message = client.api.account.messages.create(to=member_number, from_=from_number, body=sms_message)
                registered_members += 1
                time.sleep(1)

    except ApiException as e:
        return render_template('gorevli-paneli.html', api_response=api_response, exception=e)

    return render_template('gorevli-paneli.html', api_response=api_response,
                           success_message="SMS was sent to all members!", registered_members=registered_members)


@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 500

    try:
        customer = stripe.Customer.create(
            email=request.form['email'],
            source=request.form['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Vakif Bagis'
        )
    except ApiException as e:
        return render_template('donate-response.html', exception_message="Hata olustu", e=e)

    return render_template('donate-response.html', amount=amount)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
