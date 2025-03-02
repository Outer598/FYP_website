from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from view.login import login_required, manager_required, supplier_required


supplier_receipt = Blueprint("supplier_receipt", __name__)
supplier_receipt_route = apiBlueprint('supplier_receipt_route', __name__, url_prefix='/api/receipt', description='Get the suppliers receipt')

@supplier_receipt.route("/receipt")
@login_required
@supplier_required
def receipt():
    return render_template("receipt.html")
