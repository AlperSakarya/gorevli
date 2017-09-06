from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, validators, ValidationError, SelectField


class signupform(Form):
    memberName = TextField("Name")
    notificationEmail = TextField("Notification Email")
    phoneNumber = TextField("Phone Number")


class donationform(Form):
    memberName = TextField("Name")
    notificationEmail = TextField("Notification Email")
    phoneNumber = TextField("Phone Number")
    donationAmount = TextField("Donation Amount")


class LoginForm(Form):
    adminEmail = TextField("Admin Email")
    adminPassword = PasswordField("Admin Password")


class SmsForm(Form):
    sms_content = TextField("SMS content")
