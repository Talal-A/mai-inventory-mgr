from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField
from .db import getCategoryNames

def validateCategory(form, field):
	if field.data.strip() in getCategoryNames():
		raise ValidationError('Category already exists')

class Register_Category(Form):
	category = StringField('Category', [validators.Length(min=1), validateCategory])
	submit = SubmitField('Submit')
