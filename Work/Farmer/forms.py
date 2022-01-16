from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from Work.models import Farmer
from Work.Utility.utils import ValidateId

class FarmerRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    id_number = StringField('Identity Number', validators=[DataRequired(), Length(min=13, max=13)])
    password = PasswordField('Password', validators=[DataRequired()]) 
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        farmer = Farmer.query.filter_by(email = email.data).first()
        if farmer:
            raise ValidationError('Email already exist')

class UpdateFarmerProfile(FlaskForm):
    profile_picture = FileField('Profile picture', validators=[ FileAllowed(['jpg', 'png', 'jpeg'])])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    about_me = TextAreaField('About Me', validators=[Optional(strip_whitespace=True)])
    telephone = StringField('Telephone', validators=[ Length(min=10, max=10), Optional(strip_whitespace=True)])
    id_number = StringField('Identity Number', validators=[DataRequired(), Length(min=13, max=13)])
    gender = StringField('Gender', render_kw={'disabled':'disabled'}) 
    submit = SubmitField('Update')


    def validate_email(self, email):
        if current_user.email != email.data:
            farmer = Farmer.query.filter_by(email = email.data).first()
            if farmer:
                raise ValidationError('Email already exist')

    def validate_id_number(self, id_number):
        if current_user.id_number != id_number.data:
            farmer = Farmer.query.filter_by(id_number = id_number.data).first()
            if farmer:
                raise ValidationError('That identity number already exist')


class UpdateOrderStatus(FlaskForm):
    status = SelectField('Order status', validators=[DataRequired()], choices=['Received', 'Delivered', 'Cancelled'])
    submit = SubmitField('Update Status')
