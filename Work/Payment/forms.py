from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class BankDetailForm(FlaskForm):
    account_no = StringField('Account number', validators=[DataRequired(), Length(min=10, max=13)])
    branch_code = StringField('Branch code', validators=[DataRequired(), Length(min=5, max=8)])
    bank_name = SelectField('Bank name', validators=[DataRequired()], choices=['FirstRand Bank', 'Absa Bank', 'Capitec Bank', 'Nedbank Group', 'Standard Bank']) 
    submit = SubmitField('Update Banking information')
