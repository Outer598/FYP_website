from flask import render_template, Blueprint, jsonify, request, current_app, send_file
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from email.mime.text import MIMEText
import smtplib
import os
import io
from dotenv import load_dotenv, dotenv_values
from datetime import datetime
from flask.views import MethodView


external_api_route = apiBlueprint(
    'external_route', 
    __name__, 
    url_prefix='/api/external', 
    description='External API endpoints for suppliers'
)


@external_api_route.route('/all_product')
class allProduct(MethodView):
    """Get all products with their current inventory levels"""

    @external_api_route.response(200, "Products retrieved successfully")
    @external_api_route.doc(
        description="Retrieve all products with their current inventory levels",
        summary="Get all products"
    )
    def get(self):
        """
        Retrieve all products
        ---
        tags:
          - external
        responses:
          200:
            description: Products returned successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Products returned successfully
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      product_id:
                        type: integer
                        example: 1
                      product_name:
                        type: string
                        example: Product Name
                      current_stock:
                        type: integer
                        example: 100
        """
        all_product = Product.query.join(Inventory, Product.id == Inventory.product_id).all()

        all_products = [
            {
                'product_id': product.id,
                'product_name': product.product_name,
                'current_stock': product.inventory.current_stock_level,
            }
            for product in all_product
        ]
        
        return jsonify(
            {
                'message': 'Products returned successfully',
                'data': all_products
            }
        ), 200