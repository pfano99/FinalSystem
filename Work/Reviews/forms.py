from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

class ReviewForm(FlaskForm):

    body = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')
    

