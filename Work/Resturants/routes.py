from Work.Auth.routes import logout, restuarant_login
from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import current_user, login_required, logout_user
from Work.models import Favorite, Review, Restuarant, Cart, Orders, Address, Message, OrderItem
from Work.Utility.utils import SaveDocuments
from Work.Resturants.forms import UpdateRestuarantProfile
from sqlalchemy import and_, or_

from Work.Orders.forms import FilterRestOrdersForm
from Work import db

rest = Blueprint('Restuarant', __name__)


@rest.route('/restuarant/profile/<string:username>', methods=['POST', 'GET'])
@login_required
def restuarant_profile(username):
    restuarant = Restuarant.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter(and_(Review.parent==None, Review.reviewed_restuarant_id==restuarant.id))
    cart = Cart.query.filter_by(restuarant_id=current_user.id)
    orders = Orders.query.filter_by(resturant_id = restuarant.id)
    title="{}'s profile".format(restuarant.name)

    form = UpdateRestuarantProfile()
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.website.data = current_user.website
        form.telephone.data = current_user.telephone

    if form.validate_on_submit():
        current_user.telephone = form.telephone.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.website = form.website.data
        print(form.website.data)
        if form.profile_picture.data:
            current_user.profile_picture = SaveDocuments.save_profile_picture(form_picture = form.profile_picture.data)
        db.session.commit()
        flash('Your profile has been updated', 'success')
        return redirect(url_for('Restuarant.restuarant_profile', username=current_user.username))

    return render_template('Restuarant/restuarant_profile.html',orders=orders, form=form, restuarant=restuarant, reviews=reviews, title=title, cart=cart)


@rest.route('/restuarant/orders', methods=['GET', 'POST'])
@login_required
def restuarant_orders():
    if current_user.user_type != 1:
        abort(403)

    title="{}'s Dashboard".format(current_user.name)
    orders = Orders.query.filter_by(resturant_id = current_user.id)
    form = FilterRestOrdersForm()

    if form.validate_on_submit():

        orders=None
        
        from_date = None
        to_date = None

        min_price = 'o.total_cost'
        max_price = 'o.total_cost'

        if form.min_price.data != 'Any' and form.min_price.data: min_price = form.min_price.data 
        if form.max_price.data != 'Any' and form.max_price.data: max_price = form.max_price.data
        
        if form.from_date.data != None: from_date = form.from_date.data 
        if form.to_date.data != None: to_date = form.to_date.data

        if from_date is not None:
            # Thi will be executed if the orders are filtered using dates;
            # it also allows for other filters not just date
            filtered_orders = db.engine.execute(
                    """
                    SELECT o.date_ordered, o.total_cost, (SELECT COUNT(id) FROM OrderItems WHERE order_id = o.id) AS product_ordered, o.id
                    FROM orders as o
                    WHERE o.resturant_id = {}
                    AND o.date_ordered BETWEEN CAST('{}' AS DATE) AND CAST('{}' AS DATE)
                    AND o.total_cost>={}
                    AND o.total_cost<={};
                    """.format(current_user.id, from_date, to_date, min_price, max_price)
                )
        else:
            filtered_orders = db.engine.execute(
                    """
                    SELECT o.date_ordered, o.total_cost, (SELECT COUNT(id) FROM OrderItems WHERE order_id = o.id) AS product_ordered, o.id 
                    FROM orders as o 
                    WHERE o.resturant_id = {} 
                    AND o.total_cost>={}
                    AND o.total_cost<={};
                    """.format(current_user.id, min_price, max_price)
                )
        return render_template('Restuarant/rest_dashboard.html', form=form, title=title, filtered_orders=filtered_orders, orders=orders)
    
    return render_template('Restuarant/rest_dashboard.html', form=form, title=title, orders=orders)


@rest.route('/restuarant/profile/delete/confirm', methods=['GET'])
@login_required
def confirm_delete_restuarant_profile():
    return render_template('Restuarant/confirm_profile_delete.html')


@rest.route('/restuarant/profile/delete/<string:username>', methods=['POST', 'GET'])
@login_required
def delete_restuarant_profile(username):
    restuarant = Restuarant.query.filter_by(username=username).first()
    if restuarant.id != current_user.id or not current_user.is_authenticated:
        abort(400)

    orders =Orders.query.filter_by(resturant_id=restuarant.id)
    if orders:
        for order in orders:
            order_item = OrderItem.query.filter_by(order_id = order.id)
            if order_item:
                for item in order_item:
                    db.session.delete(item)
            db.session.delete(order)  

    favorite = Favorite.query.filter_by(restuarant_id=current_user.id)
    if favorite:
        for fav in favorite:
            db.session.delete(fav)

    reviews = Review.query.filter(or_(Review.reviewed_restuarant_id == restuarant.id, Review.reviewer_restuarant_id == restuarant.id))
    if reviews:
        for review in reviews:
            db.session.delete(review)

    messages = Message.query.filter_by( restuarant_id = restuarant.id)
    if messages:
        for message in messages:
            db.session.delete(message)

    addresses =Address.query.filter_by(farmer_id=restuarant.id)
    if addresses:
        for address in addresses:
            db.session.delete(address)
        
    cart =Cart.query.filter_by(restuarant_id=restuarant.id)
    if cart:
        for c in addresses:
            db.session.delete(c)
    db.session.delete(restuarant)
    db.session.commit()
    flash('Yout profile has been deleted', 'danger')

    return redirect(url_for('Main.index'))
        


@rest.route('/favorites/', methods=['POST', 'GET'])
@login_required
def favorites():
    if current_user.user_type != 1:
        abort(403)
    title = "{}'s favorite".format(current_user.name)
    farmers = Favorite.query.filter_by(restuarant_id=current_user.id)
    return render_template('Restuarant/favorites.html', title=title, farmers=farmers)



