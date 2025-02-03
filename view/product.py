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
        with_entities(Product.id, Product.product_name, Inventory.current_stock_level).all()
    
        items = []
        for item in categoryProducts:

            items.append(
                {
                    'id': item[0],
                    'name': item[1],
                    'in-stock': item[2],
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
        
        if data['productName'] == "" or data['price'] == "" or data['stockLevel'] == "" or data['reorderThreshold'] == "" or data['supplierName'] == "":
            return jsonify({"message":'Required fields not completed'}), 400
        
        supplierid = Supplier.query.filter(and_(
            Supplier.f_name.like(f"%{data['supplierName'].split(" ")[0]}%"),
            Supplier.l_name.like(f"%{data['supplierName'].split(" ")[1]}%")))\
            .with_entities(Supplier.id).first()
        
        if supplierid == None:
            return jsonify({"message": "Supplier does not exist"}), 404
        else:
            supplierid = supplierid[0]
        
        try:
            newProduct = Product(
                product_name=data['productName'].title(),
                amount_sold=0,
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
            return jsonify({"message": 'Product created successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': "Error creating product", "error": f"{str(e)}"}), 400
    

@product_route.route('/upDelProd/<int:id>')
class itemUpDel(MethodView):
    def patch(self, id):
        prodId = id
        data = request.get_json()
        print(data['original_stock_level'])
        
        if data['product_name'] == "" or data['price'] == None or data['reordering_threshold'] == "" or data['supplier_id'] == "":
            return jsonify({"message": "Required fields not completed"}), 400
        
        product = Product.query.filter_by(id=prodId).first()
        inventory = Inventory.query.filter_by(product_id=prodId).first()
        
        if product == None:
            return jsonify({"message": "Product does not exist"}), 404
        
        supplier = Supplier.query.filter(and_(Supplier.f_name.like(f"%{data['supplier_id'].split(" ")[0]}%"),
                                             Supplier.l_name.like(f"%{data['supplier_id'].split(" ")[1]}%"))).with_entities(Supplier.id).first()
        
        if supplier == None:
            return jsonify({"message": "Supplier does not exist"}), 404
        
        if   data['original_stock_level'] == None:
            data.update({'supplier_id': supplier[0],
                    })
            
            data.pop('original_stock_level')
        else:
            data.update({'supplier_id': supplier[0],
                     'current_stock_level': data['original_stock_level'] + inventory.current_stock_level,
                     'original_stock_level': data['original_stock_level'] + inventory.current_stock_level,
                     'amount_sold': inventory.original_stock_level - inventory.current_stock_level})

        try:
            for key, value in data.items():
                if hasattr(product, key):
                    if type(value) == str:
                        setattr(product, key, value.title())
                    else:
                        setattr(product, key, value)

                if hasattr(inventory, key):
                    setattr(inventory, key, value)
            
            db.session.commit()
            return jsonify({"message":"Product Updated"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating product", "Error": f"{str(e)}"}), 400

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
            