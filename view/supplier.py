from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *


supplier = Blueprint("supplier", __name__)
supplier_route = apiBlueprint('supplier_route', __name__, url_prefix='/api/supplier', description='For supplier')

@supplier.route("/supplier")
def suppliers():
    return render_template("supplier.html")



@supplier_route.route('/all_supplier')
class allSuppliers(MethodView):

    def get(self):
        all_supplier = Supplier.query.all()
        all_supplier = [{'id': supplier.id, 'name': supplier.s_name} for supplier in all_supplier]
        

        for i in all_supplier:
            products = Product.query.filter(Product.supplier_id == i['id']).all()
            i.update({'assignedProduct': len(products)})

        return jsonify(all_supplier), 200