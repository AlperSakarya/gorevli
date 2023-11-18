#!/usr/bin/env python
from __future__ import print_function
import flask, flask_login
from flask import Flask, render_template, url_for, request, json
from forms import signupform, donationform, LoginForm, SmsForm
import stripe
import uuid, json, re, time, datetime 
import auth  # I pass my access tokens here and import this auth.py file
from auth import client, auth_token, account_sid, location_id, from_number, access_token,\
    STRIPE_PUBLISHABLE_KEY_NJ, STRIPE_SECRET_KEY_NJ, STRIPE_PUBLISHABLE_KEY_DC, STRIPE_SECRET_KEY_DC, \
    users
from db import *

# Setting Global Variables
app = Flask(__name__)
app = flask.Flask(__name__)
app.secret_key = 'myverylongsecretkey' #  Change this in your production
stripe_keys = {'secret_key': STRIPE_SECRET_KEY_NJ, 'publishable_key': STRIPE_PUBLISHABLE_KEY_NJ}  # Define this in auth.py
stripe.api_key = stripe_keys['secret_key']  # Define this in auth.py. It's in your Stripe dashboard
database = "./database/member-db.sqlite3"  # This is where the DB gets put. Configured in db.py
check_create_db()  # Check and/or create the member database if does not exist. If exist will not overwrite
login_manager = flask_login.LoginManager()  # Flask login parameters
login_manager.init_app(app)  # Flask login parameters


def generate_stripe_keys(state):
    if state == "nj":
        stripe_keys = {'secret_key': STRIPE_SECRET_KEY_NJ,
                       'publishable_key': STRIPE_PUBLISHABLE_KEY_NJ}  # Define this in auth.py
        stripe.api_key = stripe_keys['secret_key']
        return stripe_keys, stripe.api_key

    if state == "dc":
        stripe_keys = {'secret_key': STRIPE_SECRET_KEY_DC,
                       'publishable_key': STRIPE_PUBLISHABLE_KEY_DC}  # Define this in auth.py
        stripe.api_key = stripe_keys['secret_key']
        return stripe_keys, stripe.api_key


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
    try:
        if form.notificationEmail.data != "":
            # Query all customers to check for existing email or phone if we do have a match, we will add
            # the credit card under their cus_ID and then charge the customer
            existing_stripe_id = (dynamo_select_all_members(form.notificationEmail.data))
            print("existing stripe_id", existing_stripe_id)
            if existing_stripe_id is False:

                try:
                    # ADD new info to local DB
                    member = (form.memberName.data, form.phoneNumber.data, form.notificationEmail.data,
                              form.location.data)
                    dynamo_cus_comm_save(member)

                except Exception as e:
                    return render_template('donate-response.html', exception_message="Error Occurred...", e=e)

            else:
                member = (form.memberName.data, form.phoneNumber.data, form.notificationEmail.data,
                          form.location.data)
                dynamo_cus_name_phone_save(member)

        else:
            return render_template('signup-response.html', exception="Email is mandatory")

        return render_template('signup-response.html', exception="", isim=form.memberName.data,
                               email=form.notificationEmail.data, telefon=form.phoneNumber.data,
                               vakif=form.location.data)

    except Exception as e:
        return render_template('signup-response.html', exception=e)


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
            members = dynamo_get_members()
            #print(members)
            if not members:
                member_count = 0
            else:
                member_count = members['Count']
                member_list = members['Items']
            return render_template('iletisim-paneli.html', api_response=member_list, registered_members=member_count)

    except Exception as e:
        return render_template('login-response.html', exception_message="Hata olustu", e=e)


@app.route('/aidatpaneli')
@flask_login.login_required
def aidat_paneli():
    api_response = ""
    total = 0
    return render_template('aidat-paneli.html', api_response=api_response,
                           registered_members=len(api_response), total=total)


@app.route('/getdonators', methods=['POST'])
@flask_login.login_required
def get_donators():
    try:
        state = request.form['state']
        generate_stripe_keys(state)
        api_response = stripe.Subscription.list(limit=100)
        total = 0
        for i in api_response['data']:
            amount = i['items']['data'][0]['plan']['amount']
            total = total + amount
        my_data = {'registered_members': len(api_response), 'total_amount': total / 100}
        json_data = json.dumps(my_data)
        return json_data
    except Exception as e:
        print("EXCEPTION!!!", e)
        return e


@app.route('/getdonatingmembers', methods=['POST'])
@flask_login.login_required
def get_donating_members():
    try:
        state = request.form['state']
        generate_stripe_keys(state)
        api_response = stripe.Subscription.list(limit=100)
        sum_response = []
        donators = {}
        for i in api_response['data']:
            email = i['items']['data'][0]['plan']['nickname']
            amount = i['items']['data'][0]['plan']['amount']
            created = i['items']['data'][0]['plan']['created']
            interval = i['items']['data'][0]['plan']['interval']
            donators["email"] = email
            donators["amount"] = amount / 100
            donators["interval"] = interval
            donators["created"] = created
            sum_response.append(json.dumps(donators))
        json_data = json.dumps(sum_response)
        return json_data
    except Exception as e:
        print("EXCEPTION!!!", e)
        return e


@app.route('/deletemember', methods=['POST'])
@flask_login.login_required
def delete_member():
    e = ""
    members = ""
    member_count = ""
    try:
        email = request.form['email']
        dynamo_delete_comm_member(email)
        members = dynamo_get_members()
        member_list = members['Items']
        if not members:
            member_count = 0
        else:
            member_count = members['Count']
    except Exception as e:
        print(e)

    return render_template('iletisim-paneli.html', api_response=member_list, registered_members=member_count, e=e)


@app.route('/deletedonator', methods=['POST'])
@flask_login.login_required
def delete_donator():
    subscription_id = request.form['subscriptionId']
    plan_id = request.form['planId']
    product_id = request.form['productId']
    customer_id = request.form['customerId']
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        sub.delete()
        plan = stripe.Plan.retrieve(plan_id)
        plan.delete()
        prod = stripe.Product.retrieve(product_id)
        prod.delete()
        cust = stripe.Customer.retrieve(customer_id)
        cust.delete()
        time.sleep(1)
        api_response = stripe.Subscription.list(limit=100)
        total = 0
        for i in api_response:
            amount = i['items']['data'][0]['plan']['amount']
            total = total + amount / 100
        success_message = "Recurring donation was removed..."
        return render_template('aidat-paneli.html', api_response=api_response,
                               registered_members=len(api_response.data), total=total, success_message=success_message)
    except Exception as e:
        return render_template('aidat-paneli.html', api_response=api_response,
                               registered_members=len(api_response.data), total=total, e=e)


@app.route('/send-sms', methods=['POST'])
def send_sms_message():
    # List customers from DB and SMS with Twilio
    # Setting from number for members
    form = SmsForm()
    sms_message = form.sms_content.data
    location = form.location.data
    try:
        members = 0
        registered_members = 0
        members = dynamo_get_members()['Items']
        for member in members:
            number = member['phone']
            number = re.sub("[^0-9]", "", str(number))
            if member['state'] == location:
                message = client.api.account.messages.create(to=number, from_=from_number, body=sms_message)
                time.sleep(1)
            registered_members += 1
    except:
        e = "There was a problem, most likely an invalid number in the member list"
        return render_template('iletisim-paneli.html', api_response=members, exception=e,
                               success_message="SMS was sent to all members!", registered_members=registered_members)

    return render_template('iletisim-paneli.html', api_response=members,
                   success_message="SMS was sent to all members!", registered_members=registered_members)


@app.route('/charge', methods=['POST'])
def charge():
    amount = int(request.form['amount']) * 100  # Converting to cents to dollars
    location = request.form['location']
    generate_stripe_keys(location)

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

                        member = (customer.id, request.form['name'], request.form['phone'], request.form['email'],
                                  request.form['location'])
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

    else:  # This means user wants recurring payments, processing them.
        #### RECURRING PAYMENTS ####
        try:
            try:  # Creating a new Stripe plan named with user's email address
                plan = stripe.Plan.create(
                    amount=amount,
                    interval="month",
                    product={
                        "name": "Monthly Donation"
                    },
                    nickname=request.form['email'],
                    currency="usd"

                )
                plan_id = plan['id']
            except stripe.InvalidRequestError as e:
                return render_template('donate-response.html', exception_message="Hata olustu", e=e)
                pass

            try:  # Checking the customer in local DB if not creating one, later this will be it's own class
                conn = create_connection(database)
                with conn:
                    # Query all customers to check for existing email or phone if we do have a match, we will add
                    # the credit card under their cus_ID and then charge the customer
                    existing_stripe_id = (select_all_members(conn, request.form['email']))

                    if existing_stripe_id:

                        # Else grab their cus_ID and make plan association to this cus_ID
                        subscribe = stripe.Subscription.create(
                            customer=existing_stripe_id,
                            items=[
                                {
                                    "plan": plan_id,
                                },
                            ]
                        )
                    else:
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

                            # ADD new customer's stripe ID to local DB
                            member = (customer.id, request.form['email'])
                            cus_id_add(conn, member)

                        except Exception as e:
                            return render_template('donate-response.html', exception_message="Hata olustu", e=e)

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
