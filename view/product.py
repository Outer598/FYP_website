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
        with_entities(Product.id, Product.product_name, Inventory.current_stock_level,Product.amount_sold,Product.price).all()

        items = []
        for item in categoryProducts:
            items.append(
                {
                    'id': item[0],
                    'name': item[1],
                    'in-stock': item[2],
                    'amount-sold': item[3],
                    'price': float(item[4])
                }
            )


        return jsonify(items), 200