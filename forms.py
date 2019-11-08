from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class ReceiveForm(FlaskForm):
	name = StringField('Name')
	bloodtype = StringField('Blood Type')
	submit = SubmitField('Search')