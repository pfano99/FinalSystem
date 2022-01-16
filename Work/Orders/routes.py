from flask import redirect, render_template, Blueprint
from Work.models import OrderItem, Orders


order = Blueprint('Order', __name__)


@order.route("/orders")
def new_orders():
    pass



