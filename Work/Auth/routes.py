from flask_login import login_user, logout_user, current_user, login_required
from flask import Blueprint, session, render_template, redirect, url_for, request, abort, flash
from flask_mail import Message
from Work.Auth.forms import FarmerLoginForm, FarmerRegistrationForm, RestuarantRegistrationForm, RestuarantLoginForm, ResetPasswordForm, RequestResetForm
from Work.models import Farmer, Restuarant
from Work import db, bcrypt, mail
from Work.Utility.utils import format_email, generate_username, ValidateId


auth = Blueprint('Auth', __name__)

@auth.route('/farmer/login/', methods = ['POST', 'GET'])
def farmer_login():
    form = FarmerLoginForm()
    if form.validate_on_submit():
        farmer = Farmer.query.filter_by(email = format_email(form.email.data)).first()
        if farmer and bcrypt.check_password_hash(farmer.password, form.password.data):
            session['account_type'] = 'farmer'
            login_user(farmer)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('Main.home'))
            
    return render_template('Auth/farmer_login.html', title = 'login', form = form)


@auth.route('/farmer/registration/',  methods = ['POST', 'GET'])
def farmer_register():
    form = FarmerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # check wether the farmer is male of female m=based on received id number
        id_number = form.id_number.data
        gender = 'Female'
        if int(id_number[6]) >= 5:
            gender = 'Male'
        
        id_n = ValidateId(id_number)

        if id_n.validation_check():

            farmer = Farmer(
                username = generate_username(form.first_name.data, form.last_name.data),
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = format_email(form.email.data),
                password = hashed_password,
                gender = gender,
                id_number = id_number

            )
            db.session.add(farmer)
            db.session.commit()
            flash('Account successfully created for {}'.format(form.first_name.data), 'success')
            return redirect(url_for('Auth.farmer_login'))
    return render_template('Auth/farmer_registration.html', title = 'Registration', form = form)


@auth.route('/restuarant/login/', methods = ['POST', 'GET'])
def restuarant_login():

    form = RestuarantLoginForm()
    if form.validate_on_submit():
        restuarant = Restuarant.query.filter_by(email = format_email(form.email.data)).first()
        if restuarant and bcrypt.check_password_hash(restuarant.password, form.password.data):
            session['account_type'] = 'restuarant'
            login_user(restuarant)
            return redirect(url_for('Main.home'))
            
    return render_template('Auth/rest_login.html', title = 'login', form = form)


@auth.route('/restuarant/registration/', methods = ['POST', 'GET'])
def restuarant_registration():
    form = RestuarantRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        website = None
        if  form.website.data:
            website=form.website.data

        restuarant = Restuarant(
            username = generate_username(form.name.data), 
            name = form.name.data,
            telephone = form.telephone.data,
            email = format_email(form.email.data),
            website = website,
            password = hashed_password,
        )
        db.session.add(restuarant)
        db.session.commit()
        flash('Account successfully created for {}'.format(form.name.data), 'success')
        return redirect(url_for('Auth.restuarant_login'))
    return render_template('Auth/rest_registration.html', title = 'Registration', form = form)


def send_reset_email(user, user_type):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='pfanosigama0@gmail.com', recipients=[user.email])
    msg.body = """ To reset your password, visit the following link: {}\n 
        if you did not make this request then ignore this email and not changes will be made 
    """.format(url_for('Auth.reset_token', token=token, _external=True, user_type=user_type)) 
    mail.send(msg)


@auth.route('/reset_password/<int:user_type>', methods=['GET', 'POST'])
def reset_request(user_type):
    if current_user.is_authenticated:
        return redirect(url_for('Main.home'))

    title = "Reset Password"
    form = RequestResetForm()
    if form.validate_on_submit():
        user = None
        if user_type == 0:
            user = Farmer.query.filter_by(email=format_email(form.email.data)).first()
        else:
            user = Restuarant.query.filter_by(email=format_email(form.email.data)).first()

        send_reset_email(user, user_type)
        flash('Email has been sent with an instruction to reset your password.', 'info')
        if user_type == 0:
            return redirect(url_for('Auth.farmer_login'))
        else:
            return redirect(url_for('Auth.restuarant_login'))

    return render_template('Auth/reset_request.html', form=form, title=title )


@auth.route('/reset_password/<token>/<int:user_type>', methods=['GET', 'POST'])
def reset_token(token, user_type):
    if current_user.is_authenticated:
        return redirect(url_for('Main.home'))
    title = "Reset Password"

    if user_type == 0:
        user = Farmer.verify_resert_token(token)
    else:
        user = Restuarant.verify_resert_token(token)

    if not user:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('Auth/reset_request', user_type=user_type))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been successfully updated, You are now able to log in.', 'success')
        if user_type == 0:
            return redirect(url_for('Auth.farmer_login'))
        else:
            return redirect(url_for('Auth.restuarant_login'))

    return render_template('Auth/reset_password.html', form=form, title=title )


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('account_type', None)
    return redirect(url_for('Main.index'))