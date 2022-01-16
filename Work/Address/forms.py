from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, HiddenField
from wtforms.validators import  DataRequired, Length, Optional, ValidationError


class AddressForm(FlaskForm):
    suburb = StringField('Suburb', validators=[DataRequired(), Length(min=3, max=100)], )
    town = StringField('Town', validators=[DataRequired(), Length(min=3, max=100)])
    city = StringField('City', validators=[Optional(strip_whitespace=True), Length(min=3, max=100)])
    lat = HiddenField('Lat', validators=[DataRequired(), Length(min=3, max=100)], id="hidden_lat")
    lng = HiddenField('Lng', validators=[DataRequired(), Length(min=3, max=100)], id="hidden_lng")
    streat_address = StringField('Streat address', validators=[Length(min=3, max=100), Optional(strip_whitespace=True)])
    building_name = StringField('Building Name', validators=[Length(min=3, max=100), Optional(strip_whitespace=True)])
    province = SelectField('Province', choices=( ['Eastern Cape', 'Free State', 'Gauteng', 'Kwazulu-Natal', 'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape', 'Western Cape']
    ))
    submit = SubmitField('Submit')

    # def validate_suburb(self, suburb):
    #     if not str(suburb.data).isalpha():
    #         raise ValidationError("Suburb should not cantain any symbols or numbers.")


    # def validate_city(self, city):
    #     if not str(city.data).isalpha():
    #         raise ValidationError("City should not cantain any symbols or numbers.")
            

    # def validate_town(self, town):
    #     if not str(town.data).isalpha():
    #         raise ValidationError("Town should not cantain any symbols or numbers.")


