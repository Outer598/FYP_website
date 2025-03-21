from flask import render_template, Blueprint, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from view.login_new import manager_required, supplier_required

description = Blueprint("description", __name__)
description_route = apiBlueprint('description_route', __name__, url_prefix='/api/description', description='Get the description of a product')

@description.route('/product/description')
@manager_required
def des():
    return render_template('description.html')


@description_route.route('/get_product_info')
class prodInfo(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        prodId = request.args.get('id')
        

        info = Product.query.join(Inventory, Product.id == Inventory.product_id)\
            .join(Supplier, Product.supplier_id == Supplier.id).filter(Product.id == prodId)\
                .first()

        productInfo = {
            'productName': info.product_name.title(),
            'SupplierName': info.supplier.s_name.title(),
            'price': info.price,
            'currentStockLevel': info.inventory.current_stock_level,
            'originalStockLevel': info.inventory.original_stock_level,
            'reorderingThreshold': info.inventory.reordering_threshold,
            'AmountSold': info.inventory.original_stock_level - info.inventory.current_stock_level
        }

        return productInfo, 200
    

@description_route.route('/monthly')
class monthlySR(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        prodId = request.args.get('id')
        
        revenue = []
        sales = []


        # Get the latest year in the database
        latest_year = db.session.query(
            func.extract('year', ProductIncome.record_date)
        ).order_by(
            func.extract('year', ProductIncome.record_date).desc()
        ).limit(1).scalar()

        # Query to get distinct months from the latest year
        monthNames = db.session.query(
            func.date_format(ProductIncome.record_date, '%M').label('month_name')  # MySQL equivalent of to_char
        ).filter(
            func.extract('year', ProductIncome.record_date) == latest_year
        ).group_by(
            func.extract('month', ProductIncome.record_date),
            func.date_format(ProductIncome.record_date, '%M')
        ).all()

        monthNames = [monthName[0] for monthName in monthNames]
        
        #to get the all the months in the current year
        months = db.session.query(
            func.extract('month', ProductIncome.record_date).label('month_number')
        ).filter(
            func.extract('year', ProductIncome.record_date) == latest_year
        ).group_by(
            func.extract('month', ProductIncome.record_date),
            func.date_format(ProductIncome.record_date, '%M')
        ).all()

        months = [month[0] for month in months]
        for month in months:
            queryData = ProductIncome.query.filter(and_(extract('month', ProductIncome.record_date)==month, 
                                            extract('year', ProductIncome.record_date)==latest_year,
                                            ProductIncome.product_id==prodId),
                                            ProductIncome.period_type=='monthly')\
                                                .all()
            
            for item in queryData:
                revenue.append(round(float(item.product_specific_income), 2))
                sales.append(item.total_units_sold)

        productMonthlyData = {
            'months': monthNames,
            'revenue': revenue,
            'sales': sales,
        }
        
        return productMonthlyData, 200

@description_route.route('/yearly')
class yearlySR(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        prodId = request.args.get('id')
        productTotalIncome = 0
        amountSold = 0
        revenue = []
        sales = []


        years = ProductIncome.query.with_entities(extract('year', ProductIncome.record_date).label('year')).distinct().limit(7)
        years =[year[0] for year in years]

        
        productYearlyData = {
            'years': years,
        }
        
        for year in years:
            amountSoldQuery = ProductIncome.query\
            .filter(and_(ProductIncome.period_type == 'monthly', ProductIncome.product_id == prodId, ProductIncome.record_date.like(f'%{year}%')))\
                .all()
            
            for items in amountSoldQuery:
                productTotalIncome += float(items.product_specific_income)
                amountSold += int(items.total_units_sold)
                
            revenue.append(round(productTotalIncome, 2))
            sales.append(round(amountSold, 2))
        
        productYearlyData.update({
            'revenue': revenue,
            'sales': sales
        })

        return jsonify(productYearlyData), 200

@description_route.route('/update')
class desUpdate(MethodView):
    @jwt_required()
    @manager_required
    def patch(self):
        proId = request.args.get('id')
        print(proId)
        data = request.get_json()
        print(data)

        product = Product.query.filter(Product.id == proId).first()
        inventory = Inventory.query.filter(Inventory.product_id == proId).first()
        for key, value in data.items():
            if value == '':
                return {'message': "Field cannot be empty"}, 400
        
        if 'current_stock_level' in data:
            stock  = Inventory.query.filter(Inventory.product_id == proId).first()
            original = stock.current_stock_level + int(data['current_stock_level'])
            data.update({
                'current_stock_level': original,
                'original_stock_level': original,
            })
        print(data)
        if 'supplier_id' in data:
            supplier_id = Supplier.query.filter(Supplier.s_name.like(f"%{data['supplier_id']}%"))\
                                                        .first()
            
            data.update({
                'supplier_id': supplier_id.id
            })
        
        try:
            for key, value in data.items():
                if hasattr(product, key):
                    if type(value) == str:
                        setattr(product, key, value.title())
                    
                    setattr(product, key, value)
                
                if hasattr(inventory, key):
                    setattr(inventory, key, value)

                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'Unable to update item', 'error': str(e)}, 404

        return {'message': 'Item updated Successfully'}, 200
        