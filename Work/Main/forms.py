from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired,  Length
from Work.models import User, Company


class AdvancedSearchForm(FlaskForm):
    province = StringField('Province', validators=[Length(min=3, max=13)])
    town = StringField('Town', validators=[Length(min=1, max=100)])
    city = StringField('City', validators=[Length(min=1, max=100)])
    job_title = StringField('Job title', validators=[DataRequired()])
    price_range = SelectField('Price Range', choices=(['Any', 'R100 - R500', 'R600 - R1000', 'R1000 - R2500', 'R2500 - R5000', 'R5000 - R10 000', 'R10 000+']))
    from_who = SelectField('From', choices=(['Individual', 'Company']))

    submit = SubmitField('Search')
