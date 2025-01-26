from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd

product = Blueprint("product", __name__)
product_route = apiBlueprint('product_route', __name__, url_prefix='/api/Products', description='Get the top three categories for sales')


@product.route('/category/product')
def product_temp():
    return render_template("product.html")


@product_route.route('/topProduct')
class topP(MethodView):

    def get(self):
        categoryId = request.args.get('id')
        topProduct = Product.query.filter_by(category_id=categoryId).\
            with_entities(Product.product_name, Product.amount_sold).\
                order_by(Product.amount_sold.desc()).limit(3).all()
        
        leastProduct = Product.query.filter_by(category_id=categoryId).\
            with_entities(Product.product_name, Product.amount_sold).\
                order_by(Product.amount_sold).limit(3).all()
        
        name = []
        amount_sold = []
        favourite = {}
        for item in topProduct:
            name.append(item[0])
            amount_sold.append(item[1])
        
        favourite.update({"topProducts": [name, amount_sold]})

        name = []
        amount_sold = []
        for item in leastProduct:
            name.append(item[0])
            amount_sold.append(item[1])
        
        favourite.update({"leastProducts": [name, amount_sold]})
        return jsonify(favourite), 200



@product_route.route('/product')
class item(MethodView):
    
    def get(self):
        categoryId = request.args.get('id')
        categoryProducts = Product.query.filter_by(category_id=categoryId).join(Inventory, Product.id==Inventory.product_id).\
        with_entities(Product.id, Product.product_name, Product.amount_sold,Product.price,  Inventory.current_stock_level, Inventory.reordering_threshold, Product.supplier_id).all()
    
        items = []
        for item in categoryProducts:
            supplerId = Supplier.query.filter_by(id=item[6]).with_entities(Supplier.f_name, Supplier.l_name).first()

            items.append(
                {
                    'id': item[0],
                    'name': item[1],
                    'amount-sold': item[2],
                    'price': float(item[3]),
                    'in-stock': item[4],
                    'reordering-threshold': item[5],
                    'supplier': f"{supplerId[0]} {supplerId[1]}"
                }
            )


        return jsonify(items), 200
    
    def post(self):
        itemId = request.args.get('id')
        data = request.get_json()
        all_products = Product.query.with_entities(Product.product_name).all()
        all_products = [item[0] for item in all_products]

        if data["productName"].title() in all_products:
            return jsonify({"message":'Item already in Database'}), 400
        
        if data['productName'] == "" or data['price'] == "" or data['stockLevel'] == "" or data['reorderThreshold'] == "":
            return jsonify({"message":'Required fields not'}), 400