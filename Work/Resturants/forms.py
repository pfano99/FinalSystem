from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from Work.models import Restuarant
    

class UpdateRestuarantProfile(FlaskForm):
    profile_picture = FileField('Profile picture', validators=[ FileAllowed(['jpg', 'png', 'jpeg'])])
    name = StringField('Restuarant name', validators=[ Length(min=3, max=100)])
    email = StringField('Email', validators=[Email()]) 
    telephone = StringField('Telephone', validators=[ Length(min=10, max=10), Optional(strip_whitespace=True)])
    website = StringField('Website', validators=[Length(min=3, max=100)])

    submit = SubmitField('Update')


    def validate_email(self, email):
        if current_user.email != email.data:
            user = Restuarant.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('Email already exist')



