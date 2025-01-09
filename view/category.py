from flask import render_template, Blueprint, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *


category = Blueprint("category", __name__)
category_route = apiBlueprint('category_route', __name__, url_prefix='/api/dashboard', description='Get the top three categories for sales')

@category.route("/category")
def categories():
    return render_template("category.html")