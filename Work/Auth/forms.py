from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from Work.models import Farmer, Restuarant
from Work import bcrypt

class FarmerRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    id_number = StringField('Identity Number', validators=[DataRequired(), Length(min=13, max=13)])
    password = PasswordField('Password', validators=[DataRequired()]) 
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        farmer = Farmer.query.filter_by(username = username.data).first()
        if farmer:
            raise ValidationError('Username already exist')

    def validate_email(self, email):
        farmer = Farmer.query.filter_by(email = email.data).first()
        if farmer:
            raise ValidationError('Email already exist')
    

class FarmerLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[DataRequired()]) 
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        farmer = Farmer.query.filter_by(email = email.data).first()
        if not farmer:
            raise ValidationError('There is no account with that email, Try signing up first.')
        
        
    def validate_password(self, password):
        farmer = Farmer.query.filter_by(email = self.email.data).first()
        if farmer:
            if not bcrypt.check_password_hash(farmer.password, password.data):
                raise ValidationError("Your password is incorrect!")



class RestuarantRegistrationForm(FlaskForm):
    name = StringField('Restuarant Name', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    telephone = StringField('Telephone', validators=[ Length(min=10, max=10)])
    website = StringField('Website', validators=[Optional(strip_whitespace=True)])
    password = PasswordField('Password', validators=[DataRequired()]) 
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        restuarant = Restuarant.query.filter_by(email = email.data).first()
        if restuarant:
            raise ValidationError('Email already exist')
    
    def validate_telephone(self, telephone):
        rest = Restuarant.query.filter_by(telephone = telephone.data).first()
        if rest:
            raise ValidationError('Telephone number is already taken, please try different one')
    

class RestuarantLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[DataRequired()]) 
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        restuarant = Restuarant.query.filter_by(email = email.data).first()
        if not restuarant:
            raise ValidationError('There is no account with that email, Try signing up first.')

    def validate_password(self, password):
        restuarant = Restuarant.query.filter_by(email = self.email.data).first()
        if restuarant:
            if not bcrypt.check_password_hash(restuarant.password, password.data):
                raise ValidationError("Your password is incorrect!")


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        farmer = Farmer.query.filter_by(email = email.data).first()
        if not farmer:
            raise ValidationError('There is no account with that email. You must register first')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

