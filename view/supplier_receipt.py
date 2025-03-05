from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
from view.login_new import manager_required, supplier_required, session


supplier_receipt = Blueprint("supplier_receipt", __name__)
supplier_receipt_route = apiBlueprint('supplier_receipt_route', __name__, url_prefix='/api/receipt', description='Get the suppliers receipt')

@supplier_receipt.route("/receipt")
@supplier_required
def receipt():
    return render_template("receipt.html")


@supplier_receipt_route.route('/receipt')
class getInvoices(MethodView):
    # Add the jwt_required decorator here
    @jwt_required()
    def get(self):
        claims = get_jwt()
        user_type = claims.get('user_type')

        to_return_data = []
        if user_type == 'supplier':
            current_user_id = claims.get("supplier_id")  # Changed from "id" to "supplier_id" based on your login_new.py
            receipt_datas = Receipt.query.filter(Receipt.supplier_id == current_user_id).all()
            to_return_data = [ {
                'id': receipt_data.id,
                'name': receipt_data.receipt_name,
                'supplier_id': receipt_data.supplier_id,
                'date': receipt_data.date_issued.strftime("%Y-%m-%d")
            } for receipt_data in receipt_datas]

        return jsonify(to_return_data), 200