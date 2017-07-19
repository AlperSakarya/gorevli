from __future__ import print_function
from flask import Flask, render_template
from forms import signupform
import squareconnect
from squareconnect.rest import ApiException
from squareconnect.apis.customers_api import CustomersApi
from squareconnect.models.create_customer_request import CreateCustomerRequest

import auth # I pass my Square access token here and import this auth.py file
# squareconnect.configuration.access_token = 'put access token here'

api_instance = CustomersApi()
app = Flask(__name__)
app.secret_key = 'myverylongsecretkey'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/charge', methods=['POST'])
def charge():
    form = signupform()
    try:
        api_response = api_instance.create_customer(CreateCustomerRequest(
            given_name=form.memberName.data,
            email_address=form.notificationEmail.data,
            phone_number=form.phoneNumber.data

        ))
        print(api_response.customer.id)
        return render_template('charge.html', exception="", isim=form.memberName.data, amount=form.donationAmount.data,
                               email=form.notificationEmail.data, telefon=form.phoneNumber.data)

    except ApiException as e:
        print(e.body)
        return render_template('charge.html', exception=e.body)


@app.route('/signup', methods=['POST'])
def signup():
    form = signupform()
    try:
        api_response = api_instance.create_customer(CreateCustomerRequest(
            given_name=form.memberName.data,
            email_address=form.notificationEmail.data,
            phone_number=form.phoneNumber.data

        ))
        print(api_response.customer.id)
        return render_template('signup.html', exception="", isim=form.memberName.data,
                               email=form.notificationEmail.data, telefon=form.phoneNumber.data)

    except ApiException as e:
        print(e.body)
        return render_template('signup.html', exception=e.body)

if __name__ == '__main__':
    app.run(debug=True)