from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField, SelectField
from .db import getCategoryNames, getItemNames, getCategories

def validateCategory(form, field):
	if field.data.strip() in getCategoryNames():
		raise ValidationError('Category already exists')

class Register_Category(Form):
	category = StringField('Category', [validators.Length(min=1), validateCategory])
	submit = SubmitField('Submit')

def validateItem(form, field):
	if field.data.strip() in getItemNames():
		raise ValidationError('Item already exists')

class Register_Item(Form):
	# TODO: Add dropdown for category selection
	category_choices = []
	for category in getCategories():
		category_choices.append((category['id'], category['name']))
	category = SelectField('Category', choices=category_choices)
	item = StringField('Item', [validators.Length(min=1), validateCategory])
	submit = SubmitField('Submit')
