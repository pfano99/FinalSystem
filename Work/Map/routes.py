from flask import Blueprint,render_template, redirect,jsonify, url_for, request
from flask_login import login_required
from Work.models import Address
import json


map = Blueprint('Map', __name__)


@map.route('/maps/')
def maps():
    # api = "AIzaSyDV2bOUGX28d0lnalwpl2MVmPHnM8w2jrc"
    adrs = Address.query.all()
    addresses = []
    for ad in adrs:
        d = {
            'id':ad.id,
            'suburb': ad.suburb,
            'town':ad.town,
            'city':ad.city,
            'province':ad.province,
            'lat':ad.latitude,
            'lng':ad.longtitude,
            'streat_address':ad.streat_address,
            'building_name':ad.building_name,
            'f_first_name': ad.farmer.first_name,
            'f_last_name':ad.farmer.last_name,
            'username':ad.farmer.username
        }
        addresses.append(d)
    return render_template('Maps/map.html', addresses=json.dumps(addresses) )


@map.route('/maps/coords/')
def maps_coords():
    # api = "AIzaSyDV2bOUGX28d0lnalwpl2MVmPHnM8w2jrc"
    adrs = Address.query.all()
    addresses = []
    for ad in adrs:
        d = {
            'id':ad.id,
            'suburb': ad.suburb,
            'town':ad.town,
            'city':ad.city,
            'province':ad.province,
            'lat':ad.latitude,
            'lng':ad.longtitude,
            'streat_address':ad.streat_address,
            'building_name':ad.building_name,
            'first_name': ad.farmer.first_name,
            'last_name':ad.farmer.last_name
        }
        addresses.append(d)

    return jsonify(addresses), 200
