from flask import flash, redirect, render_template, request, url_for, Blueprint
from sqlalchemy import func

from sqlalchemy import and_, or_
from Work.models import Product
from Work.Search.forms import AdvancedSearchForm

search = Blueprint('Search', __name__)

@search.route('/search/<string:values>', methods = ['GET', 'POST'])
def search_results(values:None):
    
    title = "{} results".format(values)
    page = request.args.get('page', 1, type=int)

    products = Product.query.filter(or_(Product.product_name.like("%{}%".format(values)))).paginate(page=page, per_page=12)

    if not products:
        return "<h3>Nothing was Found</h3>"

    form = AdvancedSearchForm()

    if form.validate_on_submit():
        min_price, max_price, min_stock = 0, 9999999, 1
        if form.min_stock.data: min_stock = int(form.min_stock.data) 
        if form.min_price.data: min_price = int(form.min_price.data) 
        if form.max_price.data: max_price = int(form.max_price.data)

        product_name = str(form.product_name.data).lower()
        product_name = product_name.lstrip()
        product_name = product_name.rstrip()
        print(product_name)
        products = Product.query.filter(and_(Product.stock_count >= min_stock, 
                func.lower(Product.product_name).ilike("%{}%".format(product_name)),
                Product.price >= min_price, Product.price <=max_price) ).paginate(page=page, per_page=12)

        return render_template('search_result.html', title = title,form=form, products = products)
    return render_template('search_result.html', title = title,form=form, products = products,)
