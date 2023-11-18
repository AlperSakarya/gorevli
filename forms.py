from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, validators, ValidationError, SelectField


class signupform(Form):
    memberName = TextAreaField("Name")
    notificationEmail = TextAreaField("Notification Email")
    phoneNumber = TextAreaField("Phone Number")
    location = TextAreaField("Vakif")


class donationform(Form):
    memberName = TextAreaField("Name")
    notificationEmail = TextAreaField("Notification Email")
    phoneNumber = TextAreaField("Phone Number")
    donationAmount = TextAreaField("Donation Amount")
    location = TextAreaField("Vakif")

class LoginForm(Form):
    adminEmail = TextAreaField("Admin Email")
    adminPassword = PasswordField("Admin Password")


class SmsForm(Form):
    sms_content = TextAreaField("SMS content")
    location = TextAreaField("Vakif")
