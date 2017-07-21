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
