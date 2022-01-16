from flask import redirect, render_template, abort, Blueprint, flash, url_for
from flask_login import login_required, current_user
from Work.models import Farmer, Restuarant, Review
from Work.Reviews.forms import ReviewForm

from Work import db

review = Blueprint('Review', __name__)


@review.route('/review/<string:username>/<int:parent_id>/<int:user_type>/', methods=['GET', 'POST'])
@login_required
def add_review(username, user_type, parent_id=None):
    # The user type tell which user is being reviewed, either a company or user.
    if user_type == 0:
        user = Farmer.query.filter_by(username=username).first_or_404()
    elif user_type == 1:
        company = Restuarant.query.filter_by(username=username).first_or_404()
    else:
        # if user_type is not one or zero, means url is not legit
        abort(404)

    
    title = "Review Page"
    form = ReviewForm()
    if form.validate_on_submit():
        if parent_id == 0:
            parent_id=None

        if user_type == 0 and current_user.user_type == 0:
            review = Review(reviewer_farmer_id=current_user.id,
                            reviewed_farmer_id=user.id, body= form.body.data, parent_id=parent_id)
        
        elif user_type == 0 and current_user.user_type == 1:
            review = Review(reviewer_restuarant_id=current_user.id,
                            reviewed_farmer_id=user.id, body= form.body.data, parent_id=parent_id)
        
        elif user_type == 1 and current_user.user_type == 1:
            review = Review(reviewer_restuarant_id=current_user.id,
                            reviewed_restuarant_id=company.id, body= form.body.data, parent_id=parent_id)
        else:
            review = Review(reviewer_farmer_id=current_user.id,
                            reviewed_restuarant_id=company.id, body= form.body.data, parent_id=parent_id)
            
        db.session.add(review)
        db.session.commit()
        flash('Your review is submitted', 'info')
        if user_type == 0:
            return redirect(url_for('Farmer.farmer_profile', username = username ))
        else:
            return redirect(url_for('Restuarant.restuarant_profile', username = username ))

    return render_template('Product/review.html', title=title, form=form)




