from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, BooleanField, TextAreaField, SubmitField, validators, ValidationError
from wtforms.validators import InputRequired

csrf = CSRFProtect()

class ContactForm(FlaskForm):
    name = StringField("Name",  [validators.InputRequired("Please enter your name.")])
    email = StringField("Email",  [validators.InputRequired("Please enter your email address."), validators.Email("Please enter your email address.")])
    subject = StringField("Subject",  [validators.InputRequired("Please enter a subject.")])
    message = TextAreaField("Message",  [validators.InputRequired("Please enter a message.")])
    submit = SubmitField("Send Message")