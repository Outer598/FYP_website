from flask import render_template, Blueprint, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd

product = Blueprint("product", __name__)
product_route = apiBlueprint('product_route', __name__, url_prefix='/api/dashboard', description='Get the top three categories for sales')


@product.route('/category/product')
def product_temp():
    return render_template("product.html")
