from flask import redirect, render_template,url_for, Blueprint
from flask.globals import request
from flask_login import current_user, login_required
from Work.models import Address
from Work.Address.forms import AddressForm
from Work import db


address = Blueprint('Address', __name__)

@address.route('/address/', methods=['POST', 'GET'])
@login_required
def address_registration():
    title = "Address Registration"
    form = AddressForm()

    if request.method == 'GET':
        if current_user.address:
            form.suburb.data = current_user.address[0].suburb
            form.town.data = current_user.address[0].town
            form.lat.data = current_user.address[0].latitude
            form.lng.data = current_user.address[0].longtitude
            form.streat_address.data = current_user.address[0].streat_address
            form.building_name.data = current_user.address[0].building_name
            form.province.data = current_user.address[0].province
            if current_user.address[0].city: form.city.data = current_user.address[0].city

    if form.validate_on_submit():

        streat_addr = None
        building_name = None
        city = None

        if form.streat_address.data: streat_addr = form.streat_address.data
        if form.building_name.data: building_name = form.building_name.data
        if form.city.data:
            city = form.city.data

        if not current_user.address:
            # if current user does not have any address information 
            # This create new address information for them
            rest_id = None
            farmer_id = None
            if current_user.user_type == 0:
                farmer_id = current_user.id
            else:
                rest_id = current_user.id
            address = Address(
                town = form.town.data,
                province = form.province.data,
                suburb = form.suburb.data,
                building_name = building_name,
                streat_address = streat_addr,
                latitude = form.lat.data,
                longtitude = form.lng.data,
                farmer_id = farmer_id,
                restuarant_id = rest_id,
                city = city
            )
            db.session.add(address)
        else:
            # if user aready have address information
            # this will update that information
            address = Address.query.get(current_user.address[0].id)
            address.suburb = form.suburb.data
            address.town = form.town.data
            address.latitude = form.lat.data
            address.longtitude = form.lng.data
            address.streat_address = streat_addr
            address.building_name = building_name
            address.province = form.province.data
            if form.city.data: address.city = city


        db.session.commit()
        if current_user.user_type == 0:
            return redirect(url_for('Farmer.farmer_profile', username = current_user.username))
        else:
            return redirect(url_for('Restuarant.restuarant_profile', username = current_user.username))

    return render_template('Product/address.html', title = title, form=form)



