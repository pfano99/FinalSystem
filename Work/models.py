from flask_migrate import branches
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import true
from Work import db, loginmanager, app
from datetime import date, datetime
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask import abort, session
from sqlalchemy import and_
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@loginmanager.user_loader
def load_user(id):
    if session['account_type'] == 'restuarant':
        return Restuarant.query.get(id)
    elif session['account_type'] == 'farmer':
        return Farmer.query.get(id)


class Farmer(db.Model, UserMixin):
    __tablename__ = "farmer"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(170), nullable = False, unique=True)
    first_name = db.Column(db.String(150), nullable = False)
    last_name = db.Column(db.String(150), nullable = False)
    about_me = db.Column(db.Text, nullable = True)
    telephone = db.Column(db.String(10), nullable = True, unique = True)
    email = db.Column(db.String(120), nullable = False, unique = True)
    profile_picture = db.Column(db.String(60), nullable = False, default = 'default.jpeg')
    gender = db.Column(db.String(6), nullable = False) 
    password = db.Column(db.String(60), nullable = False)
    id_number = db.Column(db.String(13), nullable=True, unique=True)
    is_admin = db.Column(db.Boolean, nullable = False, default=False)
    offer_services = db.Column(db.Boolean, nullable = False, default = False)
    joindate = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    user_type = db.Column(db.Boolean, nullable = False, default=0) #this is to determne if the user, is a restuarant(1), or not(0=user)

    product = db.relationship('Product', backref='farmer', lazy=True)
    address = db.relationship('Address', backref='farmer', lazy=True)
    favorite = db.relationship('Favorite', backref='farmer', lazy=True)
    bank_details = db.relationship('BankDetail', backref='farmer', lazy=True)

    messages = db.relationship('Message', backref="farmer", lazy=True)
    last_read_time = db.Column(db.DateTime)

    # reviews new approach
    reviewer = db.relationship('Review', foreign_keys='Review.reviewer_farmer_id', backref='reviewer_', lazy='dynamic')
    reviews = db.relationship('Review', foreign_keys='Review.reviewed_farmer_id', backref='reviewed_', lazy='dynamic')

    def new_messages(self,):
        last_read_time = self.last_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient = self).filter(Message.timestamp > last_read_time).count()

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'farmer_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_resert_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            farmer_id = s.loads(token)['farmer_id']
        except:
            return None  
        return Farmer.query.get(farmer_id)

    def __repr__(self,):
        return "First-Name: {}, Last-Name: {}, Email:{}".format(self.first_name, self.last_name, self.email)


class Restuarant(db.Model, UserMixin):
    __tablename__ = "restuarant"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(170), nullable = False, unique=True)
    name = db.Column(db.String(150), nullable = False)
    email = db.Column(db.String(150), nullable = False, unique=True)
    telephone = db.Column(db.String(10), nullable = False, unique=True)
    website = db.Column(db.String(250), nullable = True) 
    password = db.Column(db.String(60), nullable = False)
    date_joined = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    user_type = db.Column(db.Boolean, nullable = False, default=1) #this will be used to check if the user, is a restuarant(1), or not(0)
    profile_picture = db.Column(db.String(60), nullable = False, default = 'default.jpeg')

    # message_send = db.relationship('Message', foreign_keys='Message.comp_sender_id', backref='restuarant_author', lazy='dynamic')
    # message_received = db.relationship('Message', foreign_keys='Message.comp_recipient_id ', backref='restuarant_recipient', lazy='dynamic')
    messages = db.relationship('Message', backref="restuarant", lazy=True)
    last_read_time = db.Column(db.DateTime)

    favorite = db.relationship('Favorite', backref='restuarant', lazy=True)
    cart = db.relationship('Cart', backref='restuarant', lazy=True)
    
    address = db.relationship('Address', backref='restuarant', lazy = True)

    #Reviews 
    reviewed = db.relationship('Review', foreign_keys='Review.reviewed_restuarant_id', backref='reviewed_comp', lazy='dynamic')
    reviewer = db.relationship('Review', foreign_keys='Review.reviewer_restuarant_id', backref='reviewer_comp', lazy='dynamic')

    order = db.relationship('Orders', backref='restuarant', lazy=True )

    def exist_in_cart(self, product_id):
        return Cart.query.filter(Cart.product_id==product_id, Cart.restuarant_id == self.id ).count() > 0

    def exist_in_favorite(self, farmer_id):
        return Favorite.query.filter(Favorite.farmer_id==farmer_id, Favorite.restuarant_id == self.id ).count() > 0

    def add_to_favorite(self, farmer_id):
        if not self.exist_in_favorite(farmer_id):
            fav = Favorite(farmer_id=farmer_id, restuarant_id = self.id )
            db.session.add(fav)
            db.session.commit()

    def delete_from_favorite(self, farmer_id):
        if self.exist_in_favorite(farmer_id):
            fav = Favorite.query.filter(Favorite.farmer_id==farmer_id, Favorite.restuarant_id == self.id ).first()
            db.session.delete(fav)
            db.session.commit()

    def delete_from_cart(self, product_id):
        if self.exist_in_cart(product_id):
            cart = Cart.query.filter(Cart.product_id==product_id, Cart.restuarant_id == self.id).first()
            db.session.delete(cart)
            db.session.commit()

    def add_to_cart(self,product_id):
        if not self.exist_in_cart(product_id):
        
            cart = Cart(
                product_id = product_id,
                restuarant_id = self.id
            )
            db.session.add(cart)
            db.session.commit()

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'restuarant_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_resert_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            restuarant_id = s.loads(token)['restuarant_id']
        except:
            return None  
        return Restuarant.query.get(restuarant_id)

    def __repr__(self,):
        return "Name: {}, Category: {}, Telephone: {}".format(self.name, self.email, self.telephone)


class BankDetail(db.Model):
    __name__ = "BankDetail"
    id = db.Column(db.Integer, primary_key = True)
    account_number = db.Column(db.String(13), nullable = False, unique=True) 
    bank_name = db.Column(db.String(25), nullable = False) 
    branch_code = db.Column(db.String(8), nullable=False)

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False, unique=True)

    def __repr__(self) -> str:
        return "account number: {}, bank: {}, branch: {}".format(self.account_number, self.bank_name, self.branch_code)


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=True)
    stock_count = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    product_name = db.Column(db.String(100), nullable = False ) # apples, carrots, etc
    category = db.Column(db.String(100), nullable = False) #livestock, crops
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    offer_delivery = db.Column(db.Boolean, nullable = False, default=0) #this check if the farmer will provide delivery for the product
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable = False)
    
    images = db.relationship('Image', backref='product', lazy=True )
    cart = db.relationship('Cart', backref='product', lazy=True )
    product_item = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self,):
        return "Product: {}, Price: {}, Stock Count: {}".format(self.product_name, self.price, self.stock_count)


class Favorite(db.Model):
    __tablename__ = "Favorite"
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    restuarant_id = db.Column(db.Integer, db.ForeignKey('restuarant.id'))


class Cart(db.Model):
    __name__ = 'Cart'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    deliver_by_date = db.Column(db.DateTime, nullable=True)
    restuarant_id = db.Column(db.Integer, db.ForeignKey('restuarant.id'))


class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    restuarant_id = db.Column(db.Integer, db.ForeignKey('restuarant.id'))

    sender_type = db.Column(db.Integer, nullable=False)
    body = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self,):
        return "Body: {}".format(self.body)


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)

    reviewed_farmer_id = db.Column(db.Integer, db.ForeignKey("farmer.id"))
    reviewed_restuarant_id = db.Column(db.Integer, db.ForeignKey("restuarant.id"))
    reviewer_restuarant_id = db.Column(db.Integer, db.ForeignKey("restuarant.id"))
    reviewer_farmer_id = db.Column(db.Integer, db.ForeignKey("farmer.id"))

    parent_id = db.Column(db.Integer, db.ForeignKey("reviews.id"))
    replies = db.relationship('Review', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def add_replies(self, text):
        return Review(text=text, parent=self)

    def __repr__(self,):
        return "id: {}, body: {}, parent id: {}".format(self.id, self.body, self.parent_id )


class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    suburb = db.Column(db.String(100), nullable = True)
    town = db.Column(db.String(100), nullable = True)
    city = db.Column(db.String(100), nullable = True)
    province = db.Column(db.String(13), nullable = False)
    streat_address = db.Column(db.String(100), nullable = True)
    building_name = db.Column(db.String(100), nullable = True)
    
    latitude = db.Column(db.String(120), nullable=True)
    longtitude = db.Column(db.String(120), nullable=True)

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable = True, unique=True)
    restuarant_id = db.Column(db.Integer, db.ForeignKey('restuarant.id'), nullable = True, unique=True)
    
    def __repr__(self,):
        return "Province: {}, Town: {},  Suburb: {}".format(self.province, self.town, self.suburb)


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable = False, unique = True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable =False)

    @staticmethod
    def imgaes_limit(product_id):
        return Image.query.filter_by(product_id=product_id).count() > 5 

    def __repr__(self,):
        return "Name: {}, product id: {}".format(self.name, self.product_id)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order_details = db.relationship('OrderItem', backref='Orders', lazy=True )
    resturant_id = db.Column(db.Integer, db.ForeignKey('restuarant.id'), nullable = False)
    total_cost = db.Column(db.Integer, nullable=True)

    def __repr__(self) -> str:
        return "Date ordered: {},Total Price: {}, ".format(self.date_ordered, self.total_cost)


class OrderItem(db.Model):
    __tablename__ = 'OrderItem'
    id = db.Column(db.Integer, primary_key=True)
    deliver_by_date = db.Column(db.DateTime, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable = False, default='Pending') #shipped, Cancelled

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    def __repr__(self) -> str:
        return "Deliver by date: {}, Quantity: {}, price: {}".format(self.deliver_by_date, self.quantity, self.price)


class Credit(db.Model):
    __tablename__ = 'Credit'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    restuarant_id = db.Column(db.Integer, db.ForeignKey('restuarant.id'), nullable=False, unique=True)

    def credit_check(self, restuarant_id):
        return self.query.filter_by(restuarant_id=restuarant_id)

    def __repr__(self) -> str:
        return "Amount: {}, OrderItem: {}, Restuarant: {}".format(self.amount, self.order_item, self.restuarant_id)


class Fruits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self) -> str:
        return self.name


class Vegetables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self) -> str:
        return self.name


class AdminModelView(ModelView):
    #Authorization and Authentication for flask-admin
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        return False
    
    def not_auth(self, **kwargs):
        abort(404)
