from itertools import product
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import  DataRequired, Length, Optional

class FilterSearchForm(FlaskForm):
    searched_word = StringField('Keyword', validators=[DataRequired(), Length(min=1, max=2)])
    sort_price = SelectField('Sort Price by', choices=([ 'Lowest to Highest', 'Highest to Lowest' ]))
    province = SelectField('Province', choices=( ['Eastern Cape', 'Free State', 'Gauteng', 'Kwazulu-Natal', 'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape', 'Western Cape']
    ))
    submit = SubmitField('Search')
    

class AdvancedSearchForm(FlaskForm):
    # province = SelectField('Province', choices=( ['Eastern Cape', 'Free State', 'Gauteng', 'Kwazulu-Natal', 'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape', 'Western Cape']
    # ))
    product_name = StringField('Product Name', validators=[DataRequired()])
    min_price = IntegerField('Minimum Price', validators=[Optional(strip_whitespace=True)])
    max_price = IntegerField('Maximum Price', validators=[Optional(strip_whitespace=True)])
    min_stock = IntegerField('Minimum Stock', validators=[Optional(strip_whitespace=True)])
    delivery = SelectField('Delivery method', choices=(['Any', 'Free Delivery', 'Paid Delivery']))
    
    submit = SubmitField('Search')

