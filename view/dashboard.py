from flask import render_template, Blueprint, jsonify, url_for, request
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd
import json
from view.login_new import manager_required, supplier_required  # Import the new decorators
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

# Regular Blueprint for page routes
dashBoard = Blueprint("dashBoard", __name__)

# API Blueprint for API endpoints
dashboard_route = apiBlueprint('dashboard_route', __name__, url_prefix='/api/dashboard', 
                             description='Dashboard API endpoints')


@dashBoard.route('/manager-dashboard')
@manager_required
def manager_dashboard():
    print(request.headers)
    return render_template('index.html')


@dashBoard.route('/supplier-dashboard')
@supplier_required
def supplier_dashboard():
    print(request.headers)
    return render_template('supplier_dashboard.html')


@dashBoard.route('/auth-test')
@jwt_required()
def auth_test():
    identity = get_jwt_identity()
    claims = get_jwt()
    user_type = claims.get('user_type')
    
    return jsonify({
        'status': 'Authentication successful',
        'identity': identity,
        'user_type': user_type,
        'all_claims': claims
    })

@dashboard_route.route('/tCat')
class top_categories(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        a_decimal = 0.7
        data = {}
        years = ProductIncome.query.with_entities(extract('year',ProductIncome.record_date).label("year")).distinct().all()
        years = [year[0] for year in years]

        #to join tables product income, products and product together where the period type is equal to year and return only the product id, category id and product specific income
        test = Product.query.join(Category, Product.category_id == Category.id)\
            .join(ProductIncome, Product.id ==ProductIncome.product_id)\
                .where(ProductIncome.period_type == "yearly")\
                    .with_entities(Product.id, Category.category_name, ProductIncome.product_specific_income)\
                .all()
        
        #to store the product id, category name and product specific income in a data dictionary format
        for product_id, category_name, product_specific_income in test:
            data[product_id] = [category_name, float(product_specific_income)]
        
        #to store filer out redundant list categories
        categories = list({value[0] for value in data.values()})
        
        under_year = {}
        categories_values = []
        
        for i in categories:
            joint_category = {}
            for year in years:
                year = str(year)
                #to get the join the tables product income with the product and product table where the period type is equal to year and return only the product id, category
                sum_test = Product.query.join(Category, Product.category_id == Category.id)\
                .join(ProductIncome, Product.id ==ProductIncome.product_id)\
                    .filter(Category.category_name == i,ProductIncome.record_date.like(f"%{year}%"))\
                        .with_entities(ProductIncome.product_specific_income)\
                    .all()
                
                #to convert the list of product specific income to a float and sum them up
                categories_values = [float(income[0]) for income in sum_test]
                joint_category[year] = sum(categories_values)
            
            #to store the under_year with the joint category and the sum of product specific income in a dictionary format
            under_year[i] = joint_category
        
        top_categories = getTop3Categories(under_year, years)
        
        top_3_categories = []
        for key, value in top_categories.items():
            a_dict = []
            for total in value.values():
                a_dict.append(total)
            top_3_categories.append(
                {
                    "label": key,
                    "data": a_dict,
                }
            )
            a_decimal -= 0.2
        top_cat = {
            'years': years,
            'top3Categories': top_3_categories,
        }
        return jsonify(top_cat), 200


@dashboard_route.route('/salRev')
class SalRev(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        #to get the sales and revenue data for each year from the database
        years = ProductIncome.query.with_entities(extract('year', ProductIncome.record_date).label('year')).distinct().all()
        years = [year[0] for year in years]

        revenue = {}
        sales_data = {}
        for year in years:

            #a query to filter by the period type and year to get the total income for that year of each product
            revs = ProductIncome.query.filter(ProductIncome.period_type == 'yearly', ProductIncome.record_date.like(f"%{year}%")).with_entities(ProductIncome.product_specific_income).all()

            #a query to filter by the period type and year to get the total sales for that year of each prodict
            sales = ProductIncome.query.filter(ProductIncome.period_type == 'yearly',ProductIncome.record_date.like(f'%{year}%')).with_entities(ProductIncome.total_units_sold).all()

            #to convert the data gotten from the database to a list of floating point numbers
            revs = [float(rev[0]) for rev in revs]
            sales = [sale[0] for sale in sales]

            #to sum up the gotten sales and revenue data and store them in a dict to their corresponding year
            revenue[year] = round(sum(revs), 2)
            sales_data[year] = round(sum(sales), 2)
        #to store the years and the corresponding sales and revenue data in a dict
        sales_revenue = {
            'years': years,
            'revenue': list(revenue.values()),
            'sales': list(sales_data.values()),
        }
        
        return jsonify(sales_revenue), 200

@dashboard_route.route('/average')
class avgCash(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        # Get product info and create a mapping
        products = Product.query.with_entities(Product.id, Product.product_name).all()
        product_map = {product.id: product.product_name for product in products}
        product_ids = [product.id for product in products]

        # Weekly data
        weekly = {}
        for product_id in product_ids:
            week = ProductIncome.query.join(Product, ProductIncome.product_id == Product.id).\
            order_by(desc(ProductIncome.record_date)).filter(ProductIncome.product_id == product_id, ProductIncome.period_type == 'weekly').\
            with_entities(ProductIncome.product_specific_income).limit(4).all()
            week = [float(product[0]) for product in week]
            weekly[product_map[product_id]] = round(sum(week), 2)
        
        # Monthly data
        monthly = {}
        for product_id in product_ids:
            month = ProductIncome.query.join(Product, ProductIncome.product_id == Product.id).\
            order_by(desc(ProductIncome.record_date)).filter(ProductIncome.product_id == product_id, ProductIncome.period_type == 'monthly').\
            with_entities(ProductIncome.product_specific_income).limit(12).all()
            month = [float(product[0]) for product in month]
            monthly[product_map[product_id]] = round(sum(month), 2)

        # Yearly data
        yearly = {}
        for product_id in product_ids:
            year = ProductIncome.query.join(Product, ProductIncome.product_id == Product.id).\
            order_by(desc(ProductIncome.record_date)).filter(ProductIncome.product_id == product_id, ProductIncome.period_type == 'yearly').\
            with_entities(ProductIncome.product_specific_income).limit(7).all()
            year = [float(product[0]) for product in year]
            yearly[product_map[product_id]] = round(sum(year), 2)
        
        # Calculate averages
        weekly_avg, monthly_avg, yearly_avg = avgYrMonDay(wek=weekly, mon=monthly, year=yearly)
        
        time_periods = {
            'weekly': weekly_avg,
            'monthly': monthly_avg,
            'yearly': yearly_avg,
        }
        
        return jsonify(time_periods), 200
    

@dashboard_route.route('/five_invoice')
class allInvoice(MethodView):
    @jwt_required()
    @manager_required
    def get(self):

        invoices = Invoice.query.join(Supplier, Invoice.supplier_id == Supplier.id).order_by(Invoice.id.desc()).limit(5).all()

        invoices = [
            {'date': invoice.date_issued.strftime("%Y-%m-%d"),
             'name': invoice.invoice_name,
             'supplier_name': (invoice.supplier.s_name).title()}
        for invoice in invoices]

        return jsonify(invoices), 200  

def getTop3Categories(data:dict, years:list):
    #to get the average of each category and store it in a dictionary called categories total
    sales = pd.DataFrame.from_dict(data=data, orient="index")
    product_average_sales = round(sales.mean(axis=1), 2)
    categories_total = product_average_sales.to_dict()

    #to find the highest 3 categories and store them in a dictionary called final category
    final_category = dict(sorted(categories_total.items(), key=lambda x: x[1],reverse=True)[:3])
    final_dict = {}
    #to store the original data of the highest values
    for key, value in final_category.items():
        final_dict[key] = data[key]
    
    return final_dict


def avgYrMonDay(wek:dict, mon: dict, year: dict):
    # avg_day = round((sum(day.values())/ 7), 2)
    avg_week = round((sum(wek.values())/ 4), 2)
    avg_month = round((sum(mon.values())/ 12), 2)
    avg_year = round((sum(year.values())/ 7), 2)
    return avg_week,avg_month, avg_year