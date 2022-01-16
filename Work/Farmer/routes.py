from flask import Blueprint,render_template, redirect, url_for, request, abort, flash, jsonify, session
from flask_login import current_user, login_required, logout_user

from Work.models import Address, Farmer, Image, Message, OrderItem, Product, Review, Credit, BankDetail
from Work.Utility.utils import SaveDocuments
from Work.Farmer.forms import UpdateFarmerProfile, UpdateOrderStatus
from Work.Orders.forms import FilterOrderForm
from Work.Emails.main import Email 
from Work import db


from sqlalchemy import and_, or_

farmer = Blueprint('Farmer', __name__)


@farmer.route('/farmer/profile/<string:username>', methods=['POST', 'GET'])
@login_required
def farmer_profile(username):


    user = Farmer.query.filter_by(username=username).first_or_404()
    #this will return page not found if entered invalid username in the url.  
    #it will avoid having a blank page when username entered is not found 


    # if not user.address:
    #     if user == current_user:
    #         flash('YOU MUST ADD YOUR ADDRESS INFORMATION FIRST', 'warning')
    #         return redirect(url_for('Address.address_registration'))
    #     else:
    #         flash("Cannot Access Farmes Profile", 'warning')
    #         return redirect(url_for("Main.home"))

    products = Product.query.filter_by(farmer_id=user.id).all()
    reviews = Review.query.filter(and_(Review.parent==None, Review.reviewed_farmer_id==user.id))

    title = "{}'s profle".format(user.first_name)

    form = UpdateFarmerProfile()
    if current_user == user:
        if request.method =='GET':
            form.first_name.data = user.first_name
            form.last_name.data = user.last_name
            form.email.data = user.email
            form.gender.data = user.gender
            if current_user.telephone: 
                form.telephone.data = current_user.telephone
            if current_user.id_number: 
                form.id_number.data = current_user.id_number
            if current_user.about_me: 
                form.about_me.data = current_user.about_me

        elif request.method =='POST':
            if form.validate_on_submit():
                if form.profile_picture.data:
                    print('picture form has data')
                    current_user.profile_picture = SaveDocuments.save_profile_picture( form_picture = form.profile_picture.data)

                if form.id_number.data:
                    id_number = form.id_number.data
                    if int(id_number[6]) >= 5:
                        current_user.gender = 'Male'
                    else:
                        id_number = form.id_number.data
                        current_user.gender = 'Female'
                    current_user.id_number = form.id_number.data


                if form.telephone.data:
                    current_user.telephone = form.telephone.data

                current_user.email = form.email.data
                current_user.first_name = form.first_name.data
                current_user.last_name = form.last_name.data
                current_user.about_me = form.about_me.data
                
                db.session.commit()
                flash('Profile is Seccessfully Updated ', 'success')
                return redirect(url_for('Farmer.farmer_profile', username=current_user.username))
    return render_template('Farmer/farmer_profile.html', form=form, user=user, products=products, reviews=reviews, title = title)

def order_json(obj):
    orders = {}
    if not obj:
        return None
    else:
        m = list(obj)
        for i in m:
            orders[i[0]] = int(i[1])
    return orders

    
@farmer.route('/farmer/dashboard/<string:username>', methods=['POST', 'GET'])
@login_required
def farmer_dashboard(username):
    farmer = Farmer.query.filter_by(username=username).first()
    if not farmer or current_user != farmer:
        abort(404)
    
    title = "{}'s DashBoard".format(current_user.first_name)
    
    pie_data = None
    orders_status = None

    form = FilterOrderForm()

    if form.validate_on_submit():
        my_orders = None

        order_date=None
        min_cost = "oi.price" 
        max_cost = "oi.price" 
        status = "oi.status" 
        product_name="pd.product_name"

        if form.product_name.data: 
            product_name = "'{}'".format(form.product_name.data)

        if form.status.data and form.status.data != 'All': 
            status = "'{}'".format(form.status.data)

        if form.min_cost.data and form.min_cost.data != 'Any': 
            min_cost = form.min_cost.data

        if form.max_cost.data and form.max_cost.data != 'Any': 
            if form.max_cost.data == '10000+':
                max_cost=10000000
            else:
                max_cost = form.max_cost.data

        session['max_cost'] = max_cost 
        session['status'] = status 
        session['min_cost'] = min_cost 
        session['product_name'] = product_name
        session['order_date'] = order_date
        session['dataAvailable'] = True

        if form.order_date.data:
            query = db.engine.execute(
                """
                SELECT od.date_ordered, oi.deliver_by_date, pd.product_name, oi.quantity, oi.price, oi.status, rt.name, oi.id
                FROM OrderItems as oi, orders as od, restuarant rt, product pd
                WHERE oi.farmer_id={}
                AND od.id=oi.order_id
                AND rt.id = od.resturant_id
                AND pd.id = oi.product_id
                AND pd.product_name={}
                AND oi.price >={}
                AND oi.price <={}
                AND oi.status={}
                AND oi.quantity >={}
                AND DATE(od.date_ordered) = CAST('{}' AS DATE);
                """.format(current_user.id, product_name, min_cost, max_cost, status, "oi.quantity", form.order_date.data)
            )
        else:
            query = db.engine.execute(
                """
                SELECT od.date_ordered, oi.deliver_by_date, pd.product_name, oi.quantity, oi.price, oi.status, rt.name, oi.id
                FROM OrderItems as oi, orders as od, restuarant rt, product pd
                WHERE oi.farmer_id={}
                AND od.id=oi.order_id
                AND rt.id = od.resturant_id
                AND pd.id = oi.product_id
                AND pd.product_name={}
                AND oi.price >={}
                AND oi.price <={}
                AND oi.status={}
                AND oi.quantity >={};
                """.format(current_user.id, product_name, min_cost, max_cost, status, "oi.quantity")
            )

        return render_template('Farmer/farmer_dashboard.html',
                orders_status=orders_status,pie_data=pie_data, farmer=farmer,
                title = title, my_orders=None, form=form, filtered_orders=query
                )

    my_orders = OrderItem.query.filter_by(farmer_id=current_user.id)

    return render_template('Farmer/farmer_dashboard.html',
            orders_status=orders_status,pie_data=pie_data, farmer=farmer,
            title = title, my_orders=my_orders, form=form, filtered_orders=None
            )
    
@farmer.route('/order/update/<int:order_id>/', methods=['POST', 'GET'])
@login_required
def update_order_status(order_id):
    order = OrderItem.query.get_or_404(order_id)
    if current_user.id != order.farmer_id and current_user.user_type !=0:
        abort(400)
    title = "Update order status"
    form = UpdateOrderStatus()
    # form.status.data = order.status
    if form.validate_on_submit():
        order.status = form.status.data
        if form.status.data == 'Cancelled':
            product = Product.query.get(order.product_id)
            product.stock_count += order.quantity
            
            # Giving restuarant free credit for their next order  
            credit = None
            
            # Checking if the buyer already have credit record in the database
            credit = Credit.query.filter_by(restuarant_id = order.Orders.resturant_id).first()

            if credit:
                pass
                # # if buyer has a credit record, then we append the new credit amount to the already existing in database
                # credit.amount += order.price
                # message = """
                #     Sorry to inform you this, farmer {} {}, has cancelled your order of {} {} quantity and R{} total price.
                #     You will be receiving a refund in of a credit, you can use this credit on your next purchase. You had a credit amount of {}, Your new total 
                #     credit amount is R{}
                # """.format(current_user.first_name, current_user.last_name, product.product_name, order.quantity, order.price, (credit.amount-order.price), credit.amount )

                # email = Email()
                # email.send(app.config['MAIL_USERNAME'],app.config['MAIL_PASSWORD'], current_user.email, message)

            else:
                pass
                # else we create a new credit record in the database
                # credit = Credit(
                #     amount = order.price,
                #     restuarant_id = order.Orders.resturant_id
                # )
                # message = """
                #     Sorry to inform you this, farmer {} {}, has cancelled your order of {} {} quantity and R{} total price.
                #     You will be receiving a refund in of a credit, you can use this credit on your next purchase.Your new total 
                #     credit amount is R{}
                # """.format(current_user.first_name, current_user.last_name, product.product_name, order.quantity, order.price, credit.amount )

                # email = Email()
                # email.send(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], current_user.email, message)
            db.session.add(credit)
        db.session.commit()
        return redirect(url_for('Farmer.farmer_dashboard', username=current_user.username))
    return render_template('Farmer/updt_order_status.html',order=order, title = title, form=form)


@farmer.route('/farmer/cart/add/<int:product_id>/<string:prev_page>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id, prev_page):

    product = Product.query.get_or_404(product_id)
    if current_user.user_type != 1:
        flash('Failed to add user to cart.', 'warning')
        return redirect(url_for('Main.home'))
    current_user.add_to_cart(product_id)

    if prev_page == 'prod':
        return redirect(url_for('Product.product_info', product_id=product_id))
    else:
        return redirect(url_for('Search.search_results', values=product.product_name))
    

@farmer.route('/farmer/cart/delete/<int:product_id>/<string:prev_page>', methods=['GET', 'POST'])
@login_required
def delete_from_cart(product_id, prev_page):
    product = Product.query.get_or_404(product_id)
    
    if current_user.user_type != 1:
        flash('Failed to remove user from cart.', 'warning')
        return redirect(url_for('Main.home'))
    current_user.delete_from_cart(product_id)
    if prev_page == 'prod':
        return redirect(url_for('Product.product_info', product_id=product_id))
    elif prev_page == 'cart':
        return redirect(url_for('Product.checkout'))
    else:
        return redirect(url_for('Search.search_results', values=product.product_name))
    
@farmer.route('/farmer/favorite/add/<int:farmer_id>/', methods=['GET', 'POST'])
@login_required
def add_to_favorite(farmer_id):
    if current_user.user_type != 1:
        flash('Failed to remove user from cart.', 'warning')
        return redirect(url_for('Main.home'))
    current_user.add_to_favorite(farmer_id)
    return redirect(url_for('Main.home'))


@farmer.route('/farmer/favorite/delete/<int:farmer_id>/', methods=['GET', 'POST'])
@login_required
def delete_from_favorite(farmer_id):
    if current_user.user_type != 1:
        flash('Failed to remove user from cart.', 'warning')
        return redirect(url_for('Main.home'))
    current_user.delete_from_favorite(farmer_id)
    return redirect(url_for('Main.home'))


@farmer.route('/farmer/profile/delete/confirm/', methods=['GET'])
@login_required
def confirm_delete_profile():
    # return redirect(url_for('Farmer.delete_profile', farmer_id = farmer_id))

    return render_template('Farmer/confirm_delete.html')


@farmer.route('/farmer/profile/delete/<int:farmer_id>/', methods=['GET', 'POST'])
@login_required
def delete_profile(farmer_id):
    farmer = Farmer.query.get_or_404(farmer_id)
    if current_user != farmer:
        return abort(401) 

    products = Product.query.filter_by(farmer_id=farmer.id)
    if products:
        for product in products:
            images = Image.query.filter_by(product_id = product.id)
            if images:
                for image in images:
                    db.session.delete(image)
            orderItems = OrderItem.query.filter_by(product_id=product.id)
            if orderItems:
                for item in orderItems:
                    db.session.delete(item)
        for product in products:
            db.session.delete(product)   

    reviews = Reviews.query.filter(or_(Reviews.reviewer_farmer_id == farmer.id, Reviews.reviewed_farmer_id == farmer.id))
    if reviews:
        for review in reviews:
            db.session.delete(review)
        
    bank = BankDetail.query.filter_by(farmer_id=farmer.id)
    if bank: 
        for bnk in bank:
            db.session.delete(bnk)

    messages = Message.query.filter_by(farmer_id = farmer.id)
    if messages:
        for message in messages:
            db.session.delete(message)

    addresses =Address.query.filter_by(farmer_id=farmer.id)
    if addresses:
        for address in addresses:
            db.session.delete(address)

    
    # orders = Orders.query.filter(farmer_id = farmer.id)
    logout_user()
    db.session.delete(farmer)
    db.session.commit()
    flash('Your profile has been removed', 'danger')
    return redirect(url_for('Main.index'))
    # return render_template('Farmer/delete_product.html', farmer=farmer, title=title)
