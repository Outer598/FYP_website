from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from view.login_new import manager_required, supplier_required

product = Blueprint("product", __name__)
product_route = apiBlueprint('product_route', __name__, url_prefix='/api/Products', description='Get the top three categories for sales')


@product.route('/category/product')
@manager_required
def product_temp():
    return render_template("product.html")


@product_route.route('/topProduct')
class topP(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        categoryId = request.args.get('id')
        
        
        topProduct = Product.query.join(Inventory, Product.id == Inventory.product_id)\
        .filter(Product.category_id == categoryId).order_by(desc(Inventory.original_stock_level - Inventory.current_stock_level))\
        .limit(3).all()
        print(topProduct)
        
        leastProduct = Product.query.join(Inventory, Product.id == Inventory.product_id)\
        .filter(Product.category_id == categoryId).order_by((Inventory.original_stock_level - Inventory.current_stock_level))\
        .limit(3).all()
        print(leastProduct)
        
        name = []
        amount_sold = []
        favourite = {}
        for item in topProduct:
            name.append(item.product_name)
            amount_sold.append((item.inventory.original_stock_level) - (item.inventory.current_stock_level))
        
        favourite.update({"topProducts": [name, amount_sold]})

        name = []
        amount_sold = []
        for item in leastProduct:
            name.append(item.product_name)
            amount_sold.append((item.inventory.original_stock_level) - (item.inventory.current_stock_level))
        
        favourite.update({"leastProducts": [name, amount_sold]})
        return jsonify(favourite), 200



@product_route.route('/product')
class item(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        categoryId = request.args.get('id')
        categoryProducts = Product.query.filter_by(category_id=categoryId).join(Inventory, Product.id==Inventory.product_id)\
        .all()
    
        items = []
        for item in categoryProducts:

            items.append(
                {
                    'id': item.id,
                    'name': item.product_name,
                    'in-stock': item.inventory.current_stock_level,
                }
            )


        return jsonify(items), 200
    
    @jwt_required()
    @manager_required
    def post(self):
        itemId = request.args.get('id')
        data = request.get_json()
        all_products = Product.query.all()
        all_products = [item.product_name for item in all_products]

        if data["productName"].title() in all_products:
            return jsonify({"message":'Item already in Database'}), 400
        
        if data['productName'] == "" or data['price'] == "" or data['stockLevel'] == "" or data['reorderThreshold'] == "" or data['supplierName'] == "":
            return jsonify({"message":'Required fields not completed'}), 400
        
        supplierid = Supplier.query.filter(
            Supplier.s_name.like(f"%{data['supplierName'].split(" ")[0]}%"))\
            .with_entities(Supplier.id).first()
        
        if supplierid == None:
            return jsonify({"message": "Supplier does not exist"}), 404
        else:
            supplierid = supplierid[0]
        
        try:
            newProduct = Product(
                product_name=data['productName'].title(),
                price=data['price'],
                category_id=itemId,
                supplier_id=supplierid
            )
            db.session.add(newProduct)
            db.session.commit()

            newInventory = Inventory(
                product_id=Product.query.filter_by(product_name=data['productName'].title()).with_entities(Product.id).first()[0],
                current_stock_level=data['stockLevel'],
                original_stock_level=data['stockLevel'],
                reordering_threshold=data['reorderThreshold']
            )
            db.session.add(newInventory)
            db.session.commit()
            return jsonify({
                "message": 'Product created successfully'
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': "Error creating product", "error": f"{str(e)}"}), 400
    

@product_route.route('/upDelProd/<int:id>')
class itemUpDel(MethodView):
    @jwt_required()
    @manager_required
    def delete(self, id):
        product = Product.query.filter_by(id=id).first()

        if product == None:
            return jsonify({"message": "Product does not exist"}), 404
        
        try:
            # First, delete related inventory
            Inventory.query.filter_by(product_id=id).delete()
            
            # Then delete the product
            db.session.delete(product)
            db.session.commit()
            return jsonify({"message":"Product Deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting product", "Error": f"{str(e)}"}), 400

@product_route.route('/supplier')
class supplier(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        supplierNames = Supplier.query.all()
        supplierNames = [supplierName.s_name for supplierName in supplierNames]
        
        return jsonify({'supplierName': supplierNames}), 200
            