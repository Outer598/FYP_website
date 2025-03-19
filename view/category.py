from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from view.login_new import manager_required, supplier_required


category = Blueprint("category", __name__)
category_route = apiBlueprint('category_route', __name__, url_prefix='/api/category', description='Get the top three categories for sales')

@category.route("/category")
@manager_required
def categories():
    return render_template("category.html")


@category_route.route("/all_categories")
class Cat(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        categories = Category.query.order_by(Category.id).all()
        categories = [{"id":i.id, "label": i.category_name} for i in categories]
        for category in categories:
            item_count = len(Product.query.filter_by(category_id=category["id"]).all())
            category.update({"productCount": item_count})
        return jsonify(categories),200
    
    @jwt_required()
    @manager_required
    def post(self):
        data = request.get_json()
        print(data)
        all_categories = Category.query.all()
        all_categories = [item.category_name for item in all_categories]

        if data["categoryName"].title() in all_categories:
            return jsonify({"message": 'Item already in Database'}), 400

        if data['categoryName'] == "":
            return jsonify({"message": 'Name cannot be empty'}), 400

        try:
            newCategory = Category(category_name=data['categoryName'].title())
            db.session.add(newCategory)
            db.session.commit()
            return jsonify({
                "message": 'Category created successfully',
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': "Error creating category", "error": str(e)}), 400


@category_route.route("/upDelCat/<int:id>")
class uDCat(MethodView):
    @jwt_required()
    @manager_required
    def patch(self, id):        
        data = request.get_json()
        
        category = Category.query.filter_by(id=id).first()
        category_names = Category.query.all()
        category_names = [category_name.category_name for category_name in category_names]

        if category is None:
            return jsonify({"message": "Category does not exist"}), 404

        if data['category_name'] == "":
            return jsonify({"message": "Category Name not given"}), 400

        if data['category_name'].title() in category_names:
            return jsonify({"message": "Can't have duplicate items"}), 400

        try:
            category.category_name = data['category_name'].title()
            db.session.commit()
            return jsonify({
                "message": "Category Name Updated",
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating category", "error": str(e)}), 400
        
    @jwt_required()
    @manager_required
    def delete(self, id):
        category = Category.query.filter_by(id=id).first()

        if category is None:
            return jsonify({"message": "Category does not exist"}), 404

        try:
            db.session.delete(category)
            db.session.commit()
            return jsonify({
                "message": "Deleted Category",
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting category", "error": str(e)}), 400