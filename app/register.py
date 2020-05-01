from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField, SelectField, IntegerField, FieldList, FormField
from .db import getCategoryNames, getItemNames, getCategories

def validateCategory(form, field):
	if len(field.data.strip()) == 0:
		raise ValidationError('Category cannot be empty')
	if field.data.strip() in getCategoryNames():
		raise ValidationError('Category already exists')

class Register_Category(Form):
	category = StringField('Category', [validators.Length(min=1), validateCategory])
	submit = SubmitField('Submit')

def validateItem(form, field):
	if len(field.data.strip()) == 0:
		raise ValidationError('Item cannot be empty')
	if field.data.strip() in getItemNames():
		raise ValidationError('Item already exists')

class Register_Item(Form):
	category_choices = []
	for category in getCategories():
		category_choices.append((str(category['id']), str(category['name'])))
	category = SelectField('Category', choices=category_choices, coerce=str)
	item = StringField('Name', [validators.Length(min=1), validators.required(), validateItem])
	location = StringField('Location', [validators.Length(min=1), validators.required()])
	submit = SubmitField('Submit')

class Update_Item(Form):
	category_choices = []
	for category in getCategories():
		category_choices.append((str(category['id']), str(category['name'])))
	category = SelectField('Category', choices=category_choices, coerce=str)
	location = StringField('Location', [validators.required()])
	quantity_active = IntegerField('Quantity - Active', [validators.NumberRange(min=0, message="Minimum is 0")])
	quantity_expired = IntegerField('Quantity - Expired', [validators.NumberRange(min=0, message="Minimum is 0")])
	notes = TextAreaField('Notes')
	submit = SubmitField('Submit')
