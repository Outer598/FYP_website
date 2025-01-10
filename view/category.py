from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *


category = Blueprint("category", __name__)
category_route = apiBlueprint('category_route', __name__, url_prefix='/api/category', description='Get the top three categories for sales')

@category.route("/inventory")
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
            return jsonify({"message":'Item already in Database'}), 400
        
        if data['categoryName'] == "":
            return jsonify({"message":'Name cannot be empty'}), 400
        
        try:
            newCategory = Category(category_name=data['categoryName'].title())
            db.session.add(newCategory)
            db.session.commit()
            return jsonify({"message": 'Category created successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': "Error creating category", "error": f"{str(e)}"}), 400
