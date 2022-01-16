import os
import secrets
import random
from flask import session, abort, redirect, url_for, flash
from Work.models import Farmer
from Work import SECRET_KEY, app
import requests
import json

            
class SaveDocuments:
    @staticmethod
    def _save_in_directory(form_picture, sub_folder):
        random_name = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fullname = random_name + f_ext
        picture_path = os.path.join(app.root_path, 'static/{}'.format(sub_folder), picture_fullname)
        form_picture.save(picture_path)
        return picture_fullname
    @staticmethod
    def save_profile_picture(form_picture):
        picture_fullname = SaveDocuments._save_in_directory(form_picture, 'profile_pictures')
        return picture_fullname

    @staticmethod    
    def save_product_picture(form_picture):
        picture_fullname = SaveDocuments._save_in_directory(form_picture, 'product_images')
        return picture_fullname


def format_email(email):
    email = email.lower()
    email = email.lstrip()
    email = email.rstrip()
    return email

def generate_username(fname, lname=None):
    count = Farmer.query.count()
    count = count + random.randint(99, 900)
    if lname:
        username = "{}{}{}".format(fname, lname, count)
    else:
        username = "{}{}".format(fname, count)
    return username


def service_registered(func):
    #  This decorator will check if the Worker or Organization has already registered their Services
    # if they haven't register their services they will be rdirected to service registration page.
    #  The decorator will only be used on certain pages after the user(Worker|Organization) is logged in
    def wrapper(*args, **kwargs):
        if 'is_registered' in session:
            if  session['is_registered'] == 'False':
                return redirect(url_for('Service.register_services'))
            elif session['is_registered'] == 'True':
                f = func(*args, **kwargs)
                return f
            else:
                # if there is is_registered session on the browser but the value is not True or false
                # Something went wrong either someone tried to change the session value
                return abort(400)
        else:
            return abort(400)
    return wrapper


def generate_lat(lat):
    return "-{}".format(lat)

class ValidateId:

    def __init__(self, id_number) -> None:
        self.id_number  = id_number

    def validate_month(self,):
        if int(self.id_number[2]) > 1:
            return False
        if int(self.id_number[2]) == 1 and int(self.id_number[3]) > 2:
            return False
        if int(self.id_number[2]) == 0 and int(self.id_number[3]) == 0:
            return False
        return True


    def validate_date(self,):
        if int(self.id_number[4]) > 3:
            return False
        if int(self.id_number[4]) == 0 and int(self.id_number[5]) == 0:
            return False
        if int(self.id_number[4]) == 3 and int(self.id_number[4]) > 1:
            return False
        return True

    def is_all_digits(self,):
        for i in self.id_number:
            if not i.isdigit():
                return False
        return True

    
    def already_exist(self,):
        id_num = Farmer.query.filter_by(id_number=self.id_number).first()
        if id_num:
            return False
        return True
    
    def validation_check(self,):
        if not self.validate_month():
            flash("Identity number, Invalid month, make sure you entered the correct information", "danger")
            return False

        if not self.validate_date():
            flash("Identity number, Invalid date, make sure you entered the correct information", "danger")
            return False
        
        if not self.is_all_digits():
            flash("Identity number should only contain numbers. 0,1,2,.. 9", "danger")
            return False

        if not self.already_exist():
            flash("That identity number is already taken", "danger")
            return False

        return True


class YocoPaymentHandler:
    SECRET_KEY = 'sk_test_83531b22m9eAQRk15664867af56c'
    PUBLIC_KEY = 'pk_test_72913b53BGy8XYKed5c4'

    def charge_api(self, token, price):
        response = requests.post(
            'https://online.yoco.com/v1/charges/',
            headers={
                'X-Auth-Secret-Key': self.SECRET_KEY,
            },
            json={
                'token': token,
                'amountInCents': int(price),
                'currency': 'ZAR',
            },
            )
        return response



class PayPalPaymentHandler:
    pass


class PayFastPaymentHandler:
    pass

class OzowPaymentHandler:
    pass