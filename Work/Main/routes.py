from flask import Blueprint,render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from Work.models import Farmer
from sqlalchemy import and_
import json

main = Blueprint('Main', __name__)


@main.route('/simple/search', methods = ['GET', 'POST'])
def simple_search():
    if request.method == 'POST':
        data = request.form.get('query')
        return redirect(url_for('Search.search_results', values = data))


@main.route('/')
def index():
    title = "NextFarm"
    if current_user.is_authenticated:
        return redirect(url_for('Main.home'))
    return render_template('Main/index.html', title=title)
    

@main.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    title = "NextFarm"
    page = request.args.get('page', 1, type=int)
    farmers = Farmer.query.filter(and_(Farmer.offer_services==1, Farmer.address!=None)).paginate(page=page, per_page=12)

    if request.method == 'POST':
        data = request.form.get('query')
        return redirect(url_for('Search.search_results', values = data))

    if not current_user.address:
        flash('YOU MUST ADD YOUR ADDRESS INFORMATION FIRST', 'warning')
        return redirect(url_for('Address.address_registration'))
    
    addresses = []
    for farmer in farmers.items:
                if farmer.address:
                    address = {
                        'lat': farmer.address[0].latitude,
                        'lng': farmer.address[0].longtitude,
                        'f_first_name': farmer.first_name,
                        'f_last_name': farmer.last_name,
                        'username': farmer.username
                    }
                    addresses.append(address)
    user_address = { 'lat': current_user.address[0].latitude, 'lng': current_user.address[0].longtitude }
    print(user_address)
    return render_template('Main/home.html', farmers=farmers, title=title, addresses=json.dumps(addresses), user_address=json.dumps(user_address))


def get_addresses(products, addresses):
    if products.items:
            for product in products.items:
                if product.farmer.address:
                    address = {
                        'lat': product.farmer.address[0].latitude,
                        'lng': product.farmer.address[0].longtitude,
                        'f_first_name': product.farmer.first_name,
                        'f_last_name': product.farmer.last_name,
                        'username': product.farmer.username
                    }
                    addresses.append(address)

