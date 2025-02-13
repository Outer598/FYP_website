from flask import request, jsonify, render_template, Blueprint
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd

report_route = apiBlueprint("report_route", __name__, url_prefix= '/api/report', description = 'Generate a report based on the period returned')


@report_route.route('/')
class weeklyReport(MethodView):

    def get(self):
        prodID = Product.query.all()
        prodID = [id.id for id in prodID]
        #make this to give you the current year
        reportDates = ProductIncome.query.filter(ProductIncome.record_date.like(f"%2024%")).all()
        reportDates = [(date.record_date).strftime('%Y-%m-%d') for date in reportDates]
        
        #change the filtering condition to a variable once the first one is completed also the years 
        anItem  = ProductIncome.query.filter(and_(ProductIncome.period_type == 'weekly',
                                                  ProductIncome.product_id == prodID[0], ProductIncome.record_date == reportDates[0])).all()
        ItemUnitSold =anItem[0].total_units_sold
        ItemUnitIncome =float(anItem[0].product_specific_income)

        # Define dictionary in the given structure
        test = {
            2024: {
                'Monday': {
                    "Total unit sold": ItemUnitSold,
                    "Total unit income": ItemUnitIncome
                }
            }
        }

        year = list(test.keys())[0]

        # Convert dictionary to DataFrame
        df = pd.DataFrame.from_dict(test[2024], orient="index")

        # Rename columns to have 2024 as a header
        df.columns = pd.MultiIndex.from_product([[year], df.columns])

        # Display DataFrame
        print(df)

        return {'message': 'Report successfully generated'}, 201