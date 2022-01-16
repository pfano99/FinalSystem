from itertools import product
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField
from wtforms.validators import  DataRequired, Length, Optional, ValidationError
from flask_wtf.file import FileAllowed, FileField
from wtforms.fields.html5 import DateField
from datetime import datetime


class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass 



class UpdateProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(),])
    other = StringField('Other', default=None)
    price = StringField('Price', validators=[DataRequired()])
    stock_count = StringField('Stock Count', validators=[DataRequired()])
    category = SelectField('Category', choices=(['Category', 'Eggs', 'Fruits', 'Vegetables', 'Meat', 'Livestock']))
    delivers = SelectField('Offer delivery', choices=(['Delivers?', 'No', 'Yes']))
    description = TextAreaField('Description', validators=[Optional(strip_whitespace=True)])
    product_image = FileField('Product Picture', validators=[ FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit')

    def validate_category(self, category):
        if category.data == 'Category':
            raise ValidationError("Please choose a valid category and the name for your product.")

    def validate_delivers(self, category):
        if category.data == 'Delivers?':
            raise ValidationError("Please select the correct choice for delivery")

    def validate_product_name(self, product_name):
        
        if product_name.data == 'Other':
            if self.other.data == None:
                raise ValidationError("Please fill in the product name in the others field")


    def validate_stock_count(self, stock_count):
        if not str(stock_count.data).isdigit():
            raise ValidationError("Stock count should not contain any latters or symbols(&, !, *, etc)")

    def validate_price(self, price):
        if not str(price.data).isdigit():
            raise ValidationError("Price should not contain any latters or symbols(&, !, *, etc)")


class ProductForm(FlaskForm):
    product_name = NonValidatingSelectField('Product Name', validators=[DataRequired(),], choices=[], validate_choice=True)
    other = StringField('Other', default=None)
    price = StringField('Price', validators=[DataRequired()])
    stock_count = StringField('Stock Count', validators=[DataRequired()])
    category = SelectField('Category', choices=(['Category', 'Eggs', 'Fruits', 'Vegetables', 'Meat', 'Livestock']))
    delivers = SelectField('Offer delivery', choices=(['Delivers?', 'No', 'Yes']))
    description = TextAreaField('Description', validators=[Optional(strip_whitespace=True)])
    product_image = FileField('Product Picture', validators=[ FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit')

    def validate_category(self, category):
        if category.data == 'Category':
            raise ValidationError("Please choose a valid category and the name for your product.")

    def validate_delivers(self, category):
        if category.data == 'Delivers?':
            raise ValidationError("Please select the correct choice for delivery")

    def validate_product_name(self, product_name):
        
        if product_name.data == 'Other':
            if self.other.data == None:
                raise ValidationError("Please fill in the product name in the others field")


    def validate_stock_count(self, stock_count):
        if not str(stock_count.data).isdigit():
            raise ValidationError("Stock count should not contain any latters or symbols(&, !, *, etc)")

        if int(stock_count.data) <= 0:
            raise ValidationError('Sock count cannot be equal to zero or less.')

    def validate_price(self, price):
        if not str(price.data).isdigit():
            raise ValidationError("Price should not contain any latters or symbols(&, !, *, etc)")

        if int(price.data) <= 0:
            raise ValidationError('Price cannot be equal to zereo or less')


class UpdateCartForm(FlaskForm):
    quantity = StringField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validdate_quantity(self, quantity):
        if not str(quantity.data).isalnum():
            raise ValidationError("Quantity should not contain any numbers or sysmbols(&, !, *, etc)")


class OrderProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[], render_kw={'disabled':'disabled'})
    price = StringField('Price per kg', validators=[], render_kw={'disabled':'disabled'})
    available_stock = StringField('Available stock', validators=[], render_kw={'disabled':'disabled'})
    stock_count = StringField('Quantity', validators=[DataRequired()])
    deliver_by = DateField('Delivery by date', format='%Y-%m-%d')

    delivers = StringField('Collection date', validators=[Optional(strip_whitespace=True)])

    submit = SubmitField('Submit')

    def validate_deliver_by(self, deliver_by):
        # user_date==>date received from the form
        # system_date==>current system date
        # this will prevent user from entering date that has already passed
        user_date = str(deliver_by.data).split('-')
        system_date = datetime.utcnow().strftime('%Y-%m-%d').split('-')
        if datetime(int(user_date[0]), int(user_date[1]), int(user_date[2][0:2])) < datetime(int(system_date[0]), int(system_date[1]), int(system_date[2][0:2])):
            raise ValidationError('Invalid date, please enter date that has not yet passed')

    def validate_stock_count(self, stock_count):
        if not str(stock_count.data).isdigit():
            raise ValidationError("Quantity should not contain any letters or sysmbols(&, !, *, etc)")


        
    








