from flask.helpers import make_response
from Work.Auth.routes import restuarant_login
from flask import Blueprint, render_template,flash, redirect, url_for, request, abort, make_response, jsonify
from Work.Product.forms import ProductForm, OrderProductForm, UpdateProductForm
from Work.models import Credit, Fruits, Image, OrderItem, Product, Orders, Cart, Restuarant, Vegetables, Credit
from Work.Utility.utils import SaveDocuments, YocoPaymentHandler
from flask_login import current_user, login_required
from Work import db

prod = Blueprint('Product', __name__)

@prod.route('/product/add/', methods=['POST', 'GET'])
@login_required
def add_product():
    title = "Add Products"
    form = ProductForm()
    if not current_user.address:
        flash('YOU MUST ADD YOUR ADDRESS INFORMATION FIRST', 'warning')
        return redirect(url_for('Product.address_registration'))
        
    if form.validate_on_submit():
        
        product_name = None
        if form.product_name.data == 'others':
            product_name = form.other.data
        else:
            product_name = form.product_name.data

        product = Product(
                price = form.price.data,
                stock_count = form.stock_count.data,
                product_name = product_name,
                category = str(form.category.data),       
                offer_delivery = True if form.delivers.data == 'Yes' else False,     
                farmer_id = current_user.id,
                description = form.description.data if form.description.data else None
        )
        current_user.offer_services = True
        db.session.add(product)
        db.session.commit()

        if form.product_image.data:
            image = Image(
                product_id = product.id,
                name = SaveDocuments.save_product_picture(form.product_image.data)
            )
            db.session.add(image)
            db.session.commit()
    
        flash("New product was successfully added", 'success')
        return redirect(url_for('Product.product_info', product_id = product.id))
    return render_template("Product/product_add.html", form = form, title = title)


@prod.route('/product/category/<string:value>', methods=['POST', 'GET'])
@login_required
def category(value):
    response_data = []

    if value == 'Fruits':
        fruits = Fruits.query.all()

        for fruit in fruits:
            response_data.append( { "id" : fruit.id, "name": fruit.name })

    elif value == 'Vegetables':
        vegetables = Vegetables.query.all()
        for vegetable in vegetables:
            response_data.append( { "id" : vegetable.id, "name": vegetable.name })

    elif value == 'Eggs':
        eggs = [    
                    'Standard white eggs', 'Standard brown eggs', 'Furnished / Enriched / Nest-Laid Eggs', 
                    'Free-Run Eggs', 'Free-Range Eggs', 'Organic Eggs',  'Omega-3 Eggs', 'Vitamin-Enhanced Eggs', 
                    'Vegetarian Eggs', 'Processed Eggs', 'others'
                ]

        for i, egg in enumerate(eggs):
            response_data.append( { "id" : i, "name": egg })

    elif value == 'Livestock':
        livestock = [ 'Cattle', 'Chicken', 'Goat', 'Rabbit', 'Reindeer', 'Sheep', 'Pig', 'Zebu', 'others' ]
                
        for i, animal in enumerate(livestock):
            response_data.append( { "id" : i, "name": animal })

    elif value == 'Meat':
        livestock = [ 'Beef', 'Chicken', 'Duck', 'Goat meat', 'Lamp', 'Mutton', 'Pork', 'Turkey', 'others' ]
                
        for i, animal in enumerate(livestock):
            response_data.append( { "id" : i, "name": animal })

    else:
        pass 
    # print(response_data)
    return jsonify({'resp':response_data})


@prod.route('/product/<int:product_id>/', methods=['POST', 'GET'])
def product_info(product_id):
    title = "Product Info"
    product = Product.query.get_or_404(product_id)
    images = Image.query.filter_by(product_id=product_id)
    
    form = UpdateProductForm()
    if current_user== product.farmer:
        if request.method=='GET':
            form.price.data = str(product.price)
            form.description.data = product.description if product.description else ""
            form.stock_count.data = int(product.stock_count)
            form.product_name.data = product.product_name
            form.delivers.data = product.offer_delivery
            print(product.product_name)
            print(form.product_name.data)


        elif request.method == 'POST':
            if form.validate_on_submit():
                product.price = int(form.price.data)
                product.stock_count = form.stock_count.data
                
                product.product_name = form.product_name.data
                product.description = form.description.data

                # Update category and offer delivery information only if seller updated/changed their values 
                if not form.category.data == 'Category': product.category = str(form.category.data)

                if not form.delivers.data == 'Delivers?': 
                    if form.delivers.data == 'Yes':
                        product.offer_delivery  = True
                    else:
                        product.offer_delivery  = False

                if form.product_image.data:
                    image = Image(
                        product_id = product.id,
                        name = SaveDocuments.save_product_picture(form_picture = form.product_image.data)
                    )
                    db.session.add(image)
                else:
                    print("************Image not found************")
                
                db.session.commit()
                flash('Product Information has been updated', 'info')
                return redirect(url_for('Product.product_info', product_id=product.id))
            else:
                print("form not valid")
    return render_template('Product/product_info.html',form=form, title=title, product=product, images=images)


@prod.route('/product/delete/<int:product_id>/', methods=['POST', 'GET'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    orders = OrderItem.query.filter_by(product_id=product.id)
    cart = Cart.query.filter_by(product_id=product.id)
    if product.farmer == current_user:
        if product.images:
            for image in product.images:
                db.session.delete(image)
            db.session.commit()
        if orders:
            for order in orders:
                db.session.delete(order)
            db.session.commit()
        if cart:
            for ca in cart:
                db.session.delete(ca)
            db.session.commit()
        db.session.delete(product)
        current_user.offer_services = False if not current_user.product else True
        db.session.commit()
        flash('Product has been deleted', 'info')
        return redirect(url_for('Farmer.farmer_profile', username = current_user.username))
    else:
        abort(403)


@prod.route('/cart/update/<int:cart_id>', methods=['POST', 'GET'])
@login_required
def update_cart_info(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    product = Product.query.get_or_404(cart.product.id)
    form = OrderProductForm()
    title = "Update cart {}".format(product.product_name)

    if request.method == 'GET':
        form.product_name.data = product.product_name
        form.price.data = "R " + str(product.price) + ".00"
        form.available_stock.data = product.stock_count
        form.stock_count.data = cart.quantity
        form.delivers.data = int(product.offer_delivery)

    if form.validate_on_submit():
        if product.stock_count < int(form.stock_count.data):
            form.product_name.data = product.product_name
            form.price.data = "R " + str(product.price) + ".00"
            form.available_stock.data = product.stock_count
            form.stock_count.data = cart.quantity
            flash('The supplier does not have enough stock available', 'danger')
        else:
            # product.stock_count = product.stock_count - int(form.stock_count.data)

            cart.quantity = form.stock_count.data
            cart.deliver_by_date = form.deliver_by.data

            db.session.commit()
            return redirect(url_for('Product.checkout'))

    return render_template("Product/order_product.html", form=form, title=title)


@prod.route('/product/order-item/confirm/<int:item_id>', methods=['POST', 'GET'])
@login_required
def confirm_item_cancel(item_id):
    # this function is called when the user choose cancel option 
    # when they are in the process of making an order
    title = 'Cancel item'
    order = OrderItem.query.get_or_404(item_id)
    return render_template('Product/payment_confirmation.html', title = title, order=order)


@prod.route('/product/order/delete/<int:order_id>', methods=['GET'])
@login_required
def delete_order(order_id):
    order = Orders.query.get_or_404(order_id)
    product = Product.query.get(order.product.id)
    product.stock_count = product.stock_count + order.stock_count
    db.session.delete(order)
    db.session.commit()
    flash('Your Order was cancelled.', 'info')
    return redirect(url_for('Main.home'))

@prod.route('/confirm/<int:item_id>', methods=['GET'])
@login_required
def cancel_item(item_id):
    item = OrderItem.query.get_or_404(item_id)
    item.status = 'Cancelled'
    db.session.commit()
    flash('That item has been cancelled, Refund process will be initiated', 'warning')
    return redirect(url_for('Product.order_info', order_id = item.Orders.id))


@prod.route('/my-orders/<int:order_id>')
@login_required
def order_info(order_id):
    if current_user.user_type != 1:
        abort(403)
    title = "{}'s orders".format(current_user.name)
    orders = Orders.query.get(order_id)
    return render_template("Product/order_info.html",order_id=order_id, orders=orders,title=title)

@prod.route('/order/checkout')
@prod.route('/order/checkout/')
@login_required
def checkout():
    title = 'Checkout'
    cart = Cart.query.filter_by(restuarant_id=current_user.id)
    credit = Credit.query.filter_by(restuarant_id=current_user.id)

    credit_amount = 0.0

    # Getting the total amount of credit the restuarant have
    if credit:
        for crdt in credit:
            credit_amount +=  crdt.amount

    total = 0
    for ca in cart:
        price = ca.quantity * ca.product.price
        total += price 

    return render_template('Product/checkout.html', total=total, credit_amount=credit_amount, cart=cart, title=title)


@prod.route('/payment/methods')
@login_required
def payment_method():
    title='Payment method'
    total = 0
    cart = Cart.query.filter_by(restuarant_id=current_user.id)

    if cart.count() > 0:
        for ca in cart:
            # THis checks if all products in the cart have deliver by date set.
            # if not it will be NULL/NONE and this will be triggered
            if not ca.deliver_by_date:
                flash('Update deliver by date for {}'.format(ca.product.product_name), 'warning')
                return redirect(url_for('Product.checkout'))
    else:
        # prevent the user from proceeding to checkout if their cark is empty
        flash('Your cart is empty, you must have items in your cart to checkout.', 'danger')
        return redirect(url_for('Product.checkout'))

    for ca in cart:
        total += ca.product.price * ca.quantity


    # Check if user has credit
    credit = Credit.query.filter_by(restuarant_id = current_user.id).first()
    free_order = False

    if credit:
        if credit.amount >= total:
            free_order = True
        else:
            flash("You have a free credit for your order of R{}".format(credit.amount), 'success')
            # subtacting credit amount from the total cost
            total -= credit.amount


    # converting currency from dollars to rands
    paypal_total = int(total/14)
    
    # Converting it from cents to rands
    yoco_total = total * 100

    return render_template('Product/payment_methods.html', paypal_total = paypal_total, yoco_total=yoco_total, title=title, free_order=free_order)


@prod.route('/payments/make-order')
@login_required
def make_order():

    cart = Cart.query.filter_by(restuarant_id=current_user.id)
    if cart:
        for ca in cart:
            # THis checks if all products in the cart have deliver by date set.
            # if not it will be NULL/NONE and this will be triggered
            if not ca.deliver_by_date:
                flash('Update deliver by date for {}'.format(ca.product.product_name), 'warning')
                return redirect(url_for('Product.checkout'))

        order = Orders(resturant_id=current_user.id)
        db.session.add(order)
        db.session.commit()

        total = 0
        for ca in cart:
            order_items = OrderItem(
                deliver_by_date = ca.deliver_by_date,
                quantity = ca.quantity,
                price = ca.product.price * ca.quantity,
                farmer_id = ca.product.farmer_id,
                product_id = ca.product.id,
                order_id = order.id
            )
            ca.product.stock_count -= ca.quantity
            total += order_items.price
            db.session.add(order_items)
        order.total_cost = total
        db.session.commit()

        # clearing the cart after payment and adding items to order
        for ca in cart:
            db.session.delete(ca)
        db.session.commit()
        flash('Your order was successfully placed.', 'success')
        return redirect(url_for('Restuarant.restuarant_profile', username=current_user.username))
    else:
        return redirect(url_for('Product.checkout'))


@prod.route('/handle-yoco-payment/', methods=['POST', 'GET'])
def yoco_handler():
    data = request.get_json()
    yoco = YocoPaymentHandler()
    print(data)

    resp = yoco.charge_api(token=data['token'], price=data['price'])
    print(resp)
    if resp.status_code == 201:
        flash("Your transaction was successful", "success")
        # return redirect(url_for('Restuarant.restuarant_profile', username=current_user.username), 200)
        res = make_response("successful", 200)
        return res
    elif resp.status_code == 400:
        flash("Transaction was declined please contact your bank", "danger")
        res = make_response("decline", 400)
        return res
    else:
        flash("Something went wrong, please try agin", "danger")
        res = make_response("error", 500)
        return res
