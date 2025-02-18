from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *


category = Blueprint("category", __name__)
category_route = apiBlueprint('category_route', __name__, url_prefix='/api/category', description='Get the top three categories for sales')

@category.route("/category")
def categories():
    return render_template("category.html")


@category_route.route("/all_categories")
class Cat(MethodView):

    def get(self):
        categories = Category.query.with_entities(Category.id, Category.category_name).order_by(Category.id).all()
        categories = [{"id":i[0], "label": i[1]} for i in categories]
        for category in categories:
            item_count = len(Product.query.filter_by(category_id=category["id"]).all())
            category.update({"productCount": item_count})
        return jsonify(categories),200
    
    def post(self):
        data = request.get_json()
        all_categories = Category.query.with_entities(Category.category_name).all()
        all_categories = [item[0] for item in all_categories]

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
                "id": newCategory.id,  # Send the ID for frontend update
                "label": newCategory.category_name,
                "productCount": 0  # New category starts with zero products
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': "Error creating category", "error": str(e)}), 400


@category_route.route("/upDelCat/<int:id>")
class uDCat(MethodView):

    def patch(self, id):
        data = request.get_json()
        
        category = Category.query.filter_by(id=id).first()
        category_names = Category.query.with_entities(Category.category_name).all()
        category_names = [category_name[0] for category_name in category_names]

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
                "id": category.id,  # Send ID to match frontend
                "label": category.category_name  # Send updated name
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating category", "error": str(e)}), 400
    
    def delete(self, id):
        category = Category.query.filter_by(id=id).first()

        if category is None:
            return jsonify({"message": "Category does not exist"}), 404

        try:
            db.session.delete(category)
            db.session.commit()
            return jsonify({
                "message": "Deleted Category",
                "id": id  # Send ID to remove from UI
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting category", "error": str(e)}), 400