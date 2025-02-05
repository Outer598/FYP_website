from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd

description = Blueprint("description", __name__)
description_route = apiBlueprint('description_route', __name__, url_prefix='/api/description', description='Get the description of a product')

@description.route('/product/description')
def des():
    return render_template('description.html')


@description_route.route('/get_product_info')
class prodInfo(MethodView):

    def get(self):
        prodId = request.args.get('id')
        

        info = Product.query.join(Inventory, Product.id == Inventory.product_id)\
            .join(Supplier, Product.supplier_id == Supplier.id).filter(Product.id == prodId)\
            .with_entities(Product.product_name, Supplier.f_name, Supplier.l_name, Product.price, Inventory.current_stock_level, Inventory.original_stock_level, Inventory.reordering_threshold)\
                .all()

        productInfo = {
            'productName': info[0][0],
            'SupplierName': info[0][1] + " " + info[0][2],
            'price': info[0][3],
            'currentStockLevel': info[0][4],
            'originalStockLevel': info[0][5],
            'reorderingThreshold': info[0][6],
            'AmountSold': info[0][5] - info[0][4]
        }

        return productInfo, 200