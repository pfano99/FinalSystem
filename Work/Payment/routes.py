from flask import redirect, render_template, abort, url_for, Blueprint
from flask_login import current_user, login_required
from Work.models import BankDetail
from Work.Payment.forms import BankDetailForm
from Work import db

payment = Blueprint('Payment', __name__)

@payment.route("/payment-methods/")
def make_payment():
    pass

@payment.route('/banking-details', methods=['GET', 'POST'])
@login_required
def banking_details():
    if current_user.user_type == 1:
        abort(405)
    form = BankDetailForm()
    
    if current_user.bank_details:
        form.branch_code.data = current_user.bank_details[0].branch_code
        form.bank_name.data = current_user.bank_details[0].bank_name
        form.account_no.data = current_user.bank_details[0].account_number


    title = "Banking Details"
    if form.validate_on_submit():
        
        if current_user.bank_details:
            bank = BankDetail.query.get(current_user.bank_details[0].id)
            bank.branch_code = form.branch_code.data 
            bank.bank_name = form.bank_name.data 
            bank.account_number = form.account_no.data
        else:
            bank_info = BankDetail(
                account_number = form.account_no.data,
                bank_name = form.bank_name.data,
                branch_code = form.branch_code.data,
                farmer_id = current_user.id
            )
            db.session.add(bank_info)
        db.session.commit()
        return redirect(url_for('Farmer.farmer_profile', username=current_user.username))
    return render_template('Farmer/bank_details.html', title=title, form=form)




