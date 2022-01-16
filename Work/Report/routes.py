from flask import redirect, session, render_template, Blueprint, make_response, abort, flash
from flask_login import current_user, login_required

from io import StringIO
import csv
from datetime import datetime

from Work.models import OrderItem, db
from Work.Report.report_pdf import PDF
from Work.Report.report_csv import CsvReport

report = Blueprint('Report', __name__)


@report.route("/new-pdf-report/")
@login_required 
def generate_report_pdf():

    data = None

    if not session.get('dataAvailable'):
        data = OrderItem.query.filter_by(farmer_id=current_user.id) 
    else:
        data = db.engine.execute(
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
            """.format(current_user.id, session.get('product_name'), session.get('min_cost'), session.get('max_cost'), session.get('status'), "oi.quantity")
        )
    
    if not data:
        flash("Failed to download pdf, You do not have any orders", 'danger')
        return abort(404)
    
    pdf = PDF(orientation='L', unit='mm', format='letter')

    respond = make_response( pdf.generate_pdf(db_data=data) )
    respond.headers['Content-Type'] = 'application/pdf'

    respond.headers['Content-disposition'] = 'attachment; filename={}.pdf'.format(str(datetime.utcnow().strftime('%Y-%b-report')))

    return respond


@report.route("/restuarant/new-pdf-report/<int:order_id>")
@login_required 
def generate_report_pdf_rest(order_id):

    data = None

    data = OrderItem.query.filter_by(order_id=order_id)

    if not data:
        flash("Failed to download pdf, You do not have any orders", 'danger')
        return abort(404)

    pdf = PDF(orientation='L', unit='mm', format='letter')

    respond = make_response( pdf.generate_pdf(db_data=data) )
    respond.headers['Content-Type'] = 'application/pdf'

    respond.headers['Content-disposition'] = 'attachment; filename={}.pdf'.format(str(datetime.utcnow().strftime('%Y-%b-report')))

    return respond



@report.route("/new-csv-report/")
@login_required 
def generate_report_csv():

    data = None
    filtered = False

    if not session.get('dataAvailable'):
        data = OrderItem.query.filter_by(farmer_id=current_user.id) 
    else:
        filtered = True
        data = db.engine.execute(
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
            """.format(current_user.id, session.get('product_name'), session.get('min_cost'), session.get('max_cost'), session.get('status'), "oi.quantity")
        )
    
    if not data:
        return abort(404)


    csv_list = CsvReport()

    respond = make_response( csv_list.gen_report(data, filtered) )
    respond.headers['Content-Type'] = 'text/csv'

    respond.headers['Content-disposition'] = 'attachment; filename={}.csv'.format(str(datetime.utcnow().strftime('%Y-%b-report')))

    return respond



@report.route("/restuarant/new-csv-report/<int:order_id>")
@login_required 
def generate_report_csv_rest(order_id):

    data = None
    filtered = False

    data = OrderItem.query.filter_by(order_id=order_id)

    if not data:
        return abort(404)

    csv_list = CsvReport()

    respond = make_response( csv_list.gen_report(data, filtered) )
    respond.headers['Content-Type'] = 'text/csv'

    respond.headers['Content-disposition'] = 'attachment; filename={}.csv'.format(str(datetime.utcnow().strftime('%Y-%b-report')))

    return respond
