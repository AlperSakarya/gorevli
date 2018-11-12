#!/usr/bin/env python
from __future__ import print_function
import flask, flask_login
from flask import Flask, render_template, url_for, request
from forms import signupform, donationform, LoginForm, SmsForm
import stripe
import uuid, json, unirest, re, time, datetime
import auth  # I pass my access tokens here and import this auth.py file
from auth import client, auth_token, account_sid, location_id, from_number, access_token,\
    STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, users
from db import *

# Setting Global Variables
app = Flask(__name__)
app = flask.Flask(__name__)
app.secret_key = 'myverylongsecretkey' #  Change this in your production
stripe_keys = {'secret_key': STRIPE_SECRET_KEY, 'publishable_key': STRIPE_PUBLISHABLE_KEY}  # Define this in auth.py
stripe.api_key = stripe_keys['secret_key']  # Define this in auth.py. It's in your Stripe dashboard
database = "./database/member-db.sqlite3"  # This is where the DB gets put. Configured in db.py
check_create_db()  # Check and/or create the member database if does not exist. If exist will not overwrite
login_manager = flask_login.LoginManager()  # Flask login parameters
login_manager.init_app(app)  # Flask login parameters


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return
    user = User()
    user.id = email
    user.is_authenticated = request.form['password'] == users[email]['password']
    return user


@app.route('/')
def index():
    now = datetime.datetime.now()
    return render_template('index.html', year=now.year)


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
    conn = create_connection(database)
    with conn:
        try:
            if form.notificationEmail.data != "":
                # Query all customers to check for existing email or phone if we do have a match, we will add
                # the credit card under their cus_ID and then charge the customer
                existing_stripe_id = (select_all_members(conn, form.notificationEmail.data))
                if existing_stripe_id is False:

                    try:
                        # ADD new info to local DB
                        member = (form.memberName.data, form.phoneNumber.data, form.notificationEmail.data)
                        cus_comm_save(conn, member)

                    except Exception as e:
                        return render_template('donate-response.html', exception_message="Hata olustu", e=e)

                else:
                    member = (form.memberName.data, form.phoneNumber.data, form.notificationEmail.data)
                    cus_name_phone_save(conn, member)

            else:
                return render_template('signup-response.html', exception="Email Mecburi")

            return render_template('signup-response.html', exception="", isim=form.memberName.data,
                                   email=form.notificationEmail.data, telefon=form.phoneNumber.data)

        except Exception as e:
            return render_template('signup-response.html', exception=e.body)


@app.route('/adminlogin', methods=['POST'])
def admin_login():
    form = LoginForm()
    if form.adminEmail.data == auth.admin_Email and form.adminPassword.data == auth.admin_Password:
        user = User()
        user.id = form.adminEmail.data
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('gorevlipaneli'))
    else:
        return render_template('login-response.html', exception_message="Yanlis Bilgi Girildi")


@app.route('/gorevlipaneli')
@flask_login.login_required
def gorevlipaneli():
    return render_template('gorevli-paneli.html')


@app.route('/iletisimpaneli')
@flask_login.login_required
def iletisim_paneli():
    try:
        conn = create_connection(database)
        with conn:
            members = get_members(conn)
            if members is False:
                member_count = 0
            else:
                member_count = len(members)
            return render_template('iletisim-paneli.html', api_response=members, registered_members=member_count)
    except Exception as e:
        # username=flask_login.current_user.id We can show which user logged in to the panel by sending this to html
        return render_template('login-response.html', exception_message="Hata olustu", e=e)


@app.route('/aidatpaneli')
@flask_login.login_required
def aidat_paneli():
    try:
        api_response = stripe.Subscription.list(limit=100)
        return render_template('aidat-paneli.html', api_response=api_response,
                               registered_members=len(api_response.data))
    except Exception as e:
        # username=flask_login.current_user.id We can show which user logged in to the panel by sending this to html
        return render_template('login-response.html', exception_message="Hata olustu", e=e)


@app.route('/deletemember', methods=['POST'])
@flask_login.login_required
def delete_member():
    conn = create_connection(database)
    with conn:
        email = request.form['email']
        delete_comm_member(conn, email)
        members = get_members(conn)
        if members is False:
            member_count = 0
        else:
            member_count = len(members)
        return render_template('iletisim-paneli.html', api_response=members, registered_members=member_count)


@app.route('/send-sms', methods=['POST'])
def send_sms_message():
    # List customers from local DB and SMS with twilio
    # Setting from number for members
    form = SmsForm()
    sms_message = form.sms_content.data
    registered_members = 0
    conn = create_connection(database)
    with conn:
        try:
            members = get_members(conn)
            member_number = get_member_phones(conn)
            for number in member_number:
                number = re.sub("[^0-9]", "", str(number))
                message = client.api.account.messages.create(to=number, from_=from_number, body=sms_message)
                registered_members += 1
                time.sleep(1)

        except:
            e = "There was a problem, most likely an invalid number in the member list"
            return render_template('iletisim-paneli.html', api_response=members, exception=e,
                                   success_message="SMS was sent to all members!", registered_members=registered_members)

    return render_template('iletisim-paneli.html', api_response=members,
                           success_message="SMS was sent to all members!", registered_members=registered_members)


@app.route('/charge', methods=['POST'])
def charge():
    amount = int(request.form['amount']) * 100  # Converting to cents to dollars
    if str(request.form['recurring']) == "no":  # Checking if user wants to subscribe to monthly donations

        try:
            conn = create_connection(database)
            with conn:
                # Query all customers to check for existing email or phone if we do have a match, we will add
                # the credit card under their cus_ID and then charge the customer
                existing_stripe_id = (select_all_members(conn, request.form['email']))

                if existing_stripe_id is False:

                    try:
                        # Customer does not exist in local DB create one in Stripe
                        customer = stripe.Customer.create(
                            email=request.form['email'],
                            source=request.form['stripeToken']
                        )

                        # Using new Stripe ID to charge the customer
                        charge = stripe.Charge.create(
                            customer=customer.id,
                            amount=amount,
                            currency='usd',
                            description='Vakif Bagis'
                        )

                        # ADD new info to local DB
                        member = (customer.id, request.form['email'])
                        cus_id_save(conn, member)

                    except Exception as e:
                        return render_template('donate-response.html', exception_message="Hata olustu", e=e)

                elif existing_stripe_id is None:
                    try:
                        # Customer does not exist in local DB create one in Stripe
                        customer = stripe.Customer.create(
                            email=request.form['email'],
                            source=request.form['stripeToken']
                        )

                        # Using new Stripe ID to charge the customer
                        charge = stripe.Charge.create(
                            customer=customer.id,
                            amount=amount,
                            currency='usd',
                            description='Vakif Bagis'
                        )

                        # Adding the non/existing customer ID to the DB for existing customer
                        # Customer/Email was added via newsletter panel
                        member = (customer.id, request.form['email'])
                        cus_id_add(conn, member)

                    except Exception as e:
                        return render_template('donate-response.html', exception_message="Hata olustu", e=e)

        except Exception as e:
            return render_template('donate-response.html', exception_message="Hata olustu", e=e)

        return render_template('donate-response.html', amount=amount)

    else:  # This means user does want recurring payments, processing them.
        try:
            try:  # Creating a new Stripe plan named with user's email address
                plan_id = request.form['email']
                plan = stripe.Plan.create(
                    name="Monthly Donation",
                    id=request.form['email'],
                    interval="month",
                    currency="usd",
                    amount=amount
                )
            except stripe.InvalidRequestError as e:
                return render_template('donate-response.html', exception_message="Hata olustu", e=e)
                pass

            try:  # Checking the customer in local DB if not creating one, later this will be it's own class
                conn = create_connection(database)
                with conn:
                    # Query all customers to check for existing email or phone if we do have a match, we will add
                    # the credit card under their cus_ID and then charge the customer
                    existing_stripe_id = (select_all_members(conn, request.form['email']))

                    if existing_stripe_id is False:

                        try:
                            # Customer does not exist in local DB create one in Stripe
                            customer = stripe.Customer.create(
                                email=request.form['email'],
                                source=request.form['stripeToken']
                            )

                            # Creating a new Stripe plan named with user's email address
                            subscribe = stripe.Subscription.create(
                                customer=customer.id,
                                items=[
                                    {
                                        "plan": plan_id,
                                    },
                                ]
                            )

                            # ADD new customer to local DB
                            member = (customer.id, request.form['email'])
                            cus_id_save(conn, member)

                        except Exception as e:
                            return render_template('donate-response.html', exception_message="Hata olustu", e=e)

                    else:
                        # Else grab their cus_ID and make plan association to this cus_ID
                        subscribe = stripe.Subscription.create(
                            customer=existing_stripe_id,
                            items=[
                                {
                                    "plan": plan_id,
                                },
                            ]
                        )

            except stripe.InvalidRequestError as e:
                return render_template('donate-response.html', exception_message="Hata olustu", e=e)

        except Exception as e:
            return render_template('donate-response.html', exception_message="Hata olustu", e=e)

        return render_template('donate-response.html', amount=amount)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('donate-response.html', logout_message="Cikis Tamamlandi")


@login_manager.unauthorized_handler
def unauthorized_handler():
    e = "Unauthorized. No login credentials provided"
    return render_template('donate-response.html', exception_message="Erisim Engellendi", e=e)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
