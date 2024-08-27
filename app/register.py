from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField, SelectField, IntegerField, FieldList, FormField, RadioField
from .database import db_interface as database

def validateCategory(form, field):
	if len(field.data.strip()) == 0:
		raise ValidationError('Category cannot be empty')
	if database.exists_category_name(field.data.strip()):
		raise ValidationError('Category already exists')

class Register_Category(Form):
	category = StringField('Category', [validators.Length(min=1), validateCategory])
	submit = SubmitField('Submit')

def validateSubcategory(form, field):
	if len(field.data.strip()) == 0:
		raise ValidationError('Subcategory cannot be empty')
	if database.exists_subcategory_name(field.data.strip(), form.category.data):
		raise ValidationError('Subcategory already exists')

class Register_Subcategory(Form):
	category = SelectField('Category', choices=[], coerce=str)
	subcategory = StringField('Subcategory', [validators.Length(min=1), validateSubcategory])
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(Register_Subcategory, self).__init__(*args, **kwargs)
		category_choices = []
		for category in database.get_all_active_categories():
			category_choices.append((str(category['id']), str(category['name'])))
		self.category.choices = category_choices

def validateItem(form, field):
	if len(field.data.strip()) == 0:
		raise ValidationError('Item cannot be empty')

class Update_Item(Form):
	name = StringField('Name', [validators.DataRequired()])
	category = SelectField('Category', choices=[], coerce=str, id="category_choice")
	location = StringField('Location', [validators.DataRequired()])
	url = StringField('URL')
	quantity_active = IntegerField('Quantity - Active', [validators.NumberRange(min=0, max= 2147483647, message="Quantity must be between 0 and 2.147b")], default=0)
	quantity_expired = IntegerField('Quantity - Expired', [validators.NumberRange(min=0, max= 2147483647, message="Quantity must be between 0 and 2.147b")], default=0)
	notes_public = TextAreaField('Notes')
	notes_private = TextAreaField('Notes - Internal')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(Update_Item, self).__init__(*args, **kwargs)
		category_choices = []
		for category in database.get_all_active_categories():
			for subcategory in database.get_all_active_subcategories_for_category(category['id']):
				category_choices.append((str(category['id'] + "," + subcategory['id']), str(category['name'] + " > " + subcategory['name'])))
		self.category.choices = category_choices

class Search_QuantityUpdate(Form): 
	selectInput = SelectField('Select an item:', choices=[], validators=[validators.InputRequired()])
	quantity = IntegerField('Quantity', [validators.NumberRange(min=-2147483647, max= 2147483647, message="Quantity must be between -2.147b and 2.147b")], default=0)
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(Search_QuantityUpdate, self).__init__(*args, **kwargs)
		item_choices = [("", "")] + [(str(item['id']), str(item['name']) + " [" + str(item['location']) + "]") for item in database.get_all_items()]
		self.selectInput.choices = item_choices
