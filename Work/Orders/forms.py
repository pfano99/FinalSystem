from flask_wtf import FlaskForm
from wtforms.validators import Optional, ValidationError
from wtforms import SelectField, SubmitField, StringField
from wtforms.fields.html5 import DateField

from datetime  import datetime


class FilterOrderForm(FlaskForm):
    order_date = DateField('Date Ordered', validators=[Optional(strip_whitespace=True)],  format='%Y-%m-%d')
    deliver_by = DateField('Delivery by date', validators=[Optional(strip_whitespace=True)], format='%Y-%m-%d')
    product_name = StringField('Product name', validators=[Optional(strip_whitespace=True)])
    min_cost = StringField('Minimun Cost', validators=[Optional(strip_whitespace=True)])
    max_cost = StringField('Maximum Cost', validators=[Optional(strip_whitespace=True)])
    status = SelectField('Order status', validators=[Optional(strip_whitespace=True)], choices=['All', 'Pending', 'Received', 'Delivered', 'Cancelled'])
    submit = SubmitField('Filter')

    def validate_min_cost(self, min_cost):
        if not str(min_cost.data).isdigit():
            raise ValidationError("Minimun cost cannot contain letters or symbols($,%, etc) ")
        
        if self.max_cost:
            if str(self.max_cost.data).isdigit() and int(self.max_cost.data) < int(min_cost.data):
                raise ValidationError("Minimun cost cannot be greater than the maximun cost")

    def validate_max_cost(self, max_cost):
        if not str(max_cost.data).isdigit():
            raise ValidationError("Maximum cost cannot contain letters or symbols($,%, etc) ")
        

class FilterRestOrdersForm(FlaskForm):
    from_date = DateField('From date', validators=[Optional(strip_whitespace=True)],  format='%Y-%m-%d')
    to_date = DateField('To date', validators=[Optional(strip_whitespace=True)],  format='%Y-%m-%d')
    min_price = StringField('Minimum cost', validators=[Optional(strip_whitespace=True)])
    max_price = StringField('Maximum cost', validators=[Optional(strip_whitespace=True)])
    submit = SubmitField('Filter')

    def validate_min_price(self, min_price):
        if not str(min_price.data).isdigit():
            raise ValidationError("Minimun cost cannot contain letters or symbols($,%, etc) ")
        
        if self.max_price:
            if str(self.max_price.data).isdigit() and int(self.max_price.data) < int(min_price.data):
                raise ValidationError("Minimun cost cannot be greater than the maximun cost")

    def validate_max_price(self, max_price):
        if not str(max_price.data).isdigit():
            raise ValidationError("Maximum price cannot contain letters or symbols($,%, etc) ")


    def validate_from_date(self, from_date):
        if from_date.data and self.to_date.data is None:
            raise ValidationError('Both from and to dates are needed')

    def validate_to_date(self, to_date):
        if to_date.data and self.from_date.data is None:
            raise ValidationError('Both from and to dates are needed')

        # prevent the user from entering to_date that is less than from date
        print(self.to_date.data)
        to_date = str(to_date.data).split('-')
        from_date = str(self.from_date.data).split('-')

        if datetime(int(to_date[0]), int(to_date[1]), int(to_date[2])) < datetime(int(from_date[0]), int(from_date[1]), int(from_date[2])):
            raise ValidationError("'To date' cannot be greater than 'from date'!!!")
