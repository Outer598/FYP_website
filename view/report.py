from flask import request, jsonify, render_template, Blueprint
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
import pandas as pd
from datetime import datetime, timedelta
import os

report_route = apiBlueprint("report_route", __name__, url_prefix= '/api/report', description = 'Generate a report based on the period returned')


@report_route.route('/')
class weeklyReport(MethodView):

    def get(self):
         # Get all product IDs from the database
        prodID = Product.query.all()
        prodID = [id.id for id in prodID]

        # Get the most recent year from the ProductIncome records
        latest_year = db.session.query(
            func.extract('year', ProductIncome.record_date)
        ).order_by(
            func.extract('year', ProductIncome.record_date).desc()
        ).limit(1).scalar()

        # Get current month
        month = datetime.now().month

        # Initialize empty dictionaries to store the data
        sheetData = {}

        # Loop through each product ID
        for id in prodID:
            # Query weekly records for current product
            anItem = ProductIncome.query.filter(and_(
                ProductIncome.period_type == 'weekly',
                ProductIncome.product_id == id,
                extract("month", ProductIncome.record_date) == month,
                ProductIncome.record_date.like(f"%{latest_year}%")
            )).all()

            weekCount = 1
            productName = Product.query.filter(Product.id == id).first()
            
            if not productName:
                continue

            test = {
                productName.product_name: {}
            }

            total_units = 0
            total_income = 0

            # Initialize all weeks with zero values
            for week_num in range(1, 5):  # Assuming 4 weeks per month
                test[productName.product_name][f'week {week_num}'] = {
                    'Total unit sold': 0,
                    'Total unit income': 0.0
                }

            # Process each week's data
            for week in anItem:
                stuff = {
                    f'week {weekCount}': {
                        'Total unit sold': week.total_units_sold or 0,
                        'Total unit income': float(week.product_specific_income or 0),
                    }
                }
                total_units += week.total_units_sold or 0
                total_income += float(week.product_specific_income or 0)
                test[productName.product_name].update(stuff)
                weekCount += 1

            # Add product totals
            test[productName.product_name]['Product Totals'] = {
                'Total unit sold': total_units,
                'Total unit income': total_income
            }

            sheetData.update(test)

        # Create initial DataFrame
        df = pd.DataFrame.from_dict(sheetData, orient='index')

        # Create a new DataFrame with better structure
        structured_df = pd.DataFrame(index=df.index)

        # Process each column (week) separately
        for column in df.columns:
            if column != 'Product Totals':
                # Extract units sold and income into separate columns with error handling
                structured_df[f'{column} - Units'] = df[column].apply(
                    lambda x: x.get('Total unit sold', 0) if isinstance(x, dict) else 0
                )
                structured_df[f'{column} - Income'] = df[column].apply(
                    lambda x: x.get('Total unit income', 0.0) if isinstance(x, dict) else 0.0
                )

        # Add product totals
        structured_df['Total Units'] = df['Product Totals'].apply(
            lambda x: x.get('Total unit sold', 0) if isinstance(x, dict) else 0
        )
        structured_df['Total Income'] = df['Product Totals'].apply(
            lambda x: x.get('Total unit income', 0.0) if isinstance(x, dict) else 0.0
        )

        # Calculate weekly totals
        weekly_totals = {}
        for column in structured_df.columns:
            if 'Units' in column or 'Income' in column:
                weekly_totals[column] = structured_df[column].sum()

        # Add weekly totals row
        structured_df.loc['Weekly Totals'] = weekly_totals

        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'weekly_sales_report_{timestamp}.xlsx'

        # Create full file path (put this in your desired directory)
        file_path = os.path.join('C:/Users/james/OneDrive/Documents/Babcock/project/FYP/Main project chapters/FYP_website/view', filename)

        # Create Excel writer object
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            # Write DataFrame to Excel
            structured_df.to_excel(writer, sheet_name='Sales Report')
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Sales Report']
            
            # Add formatting
            money_format = workbook.add_format({'num_format': '₦#,##0.00'})
            number_format = workbook.add_format({'num_format': '#,##0'})
            
            # Apply formatting to columns
            for col_num, column in enumerate(structured_df.columns):
                max_length = max(
                    structured_df[column].astype(str).apply(len).max(),
                    len(column)
                )
                worksheet.set_column(col_num + 1, col_num + 1, max_length + 2)
                
                if 'Income' in column:
                    worksheet.set_column(col_num + 1, col_num + 1, max_length + 2, money_format)
                elif 'Units' in column:
                    worksheet.set_column(col_num + 1, col_num + 1, max_length + 2, number_format)

        return jsonify({'message': f'Report generated: {filename}'}), 201

@report_route.route('/monthly')
class monthlyReport(MethodView):

    def get(self):
         # Get all product IDs from the database
        prodID = Product.query.all()
        prodID = [id.id for id in prodID]

        # Get the most recent year from the ProductIncome records
        latest_year = db.session.query(
            func.extract('year', ProductIncome.record_date)
        ).order_by(
            func.extract('year', ProductIncome.record_date).desc()
        ).limit(1).scalar()

        # Step 1: Get the most recent date in the database
        latest_date = db.session.query(func.max(ProductIncome.record_date)).scalar()

        if not latest_date:
            return []  # No data in the database

        # Step 2: Calculate the date 6 months before the latest date
        six_months_ago = latest_date - timedelta(days=180)

        # Step 3: Query the unique months in the last 6 months, ordered by calendar order
        last_six_months = (
            db.session.query(extract('month', ProductIncome.record_date))  # Get month number
            .filter(ProductIncome.record_date >= six_months_ago)  # Filter last 6 months
            .group_by(extract('month', ProductIncome.record_date))  # Get unique months
            .order_by(extract('month', ProductIncome.record_date))  # Order in calendar order
            .all()
        )

        # Convert month numbers to month names
        monthNames = list(reversed([datetime.strptime(str(month[0]), "%m").strftime("%B") for month in last_six_months]))
        
        

        # Initialize empty dictionaries to store the data
        sheetData = {}

        # Loop through each product ID
        for id in prodID:
            # Query monthly records for current product
            anItem = ProductIncome.query.filter(and_(
                ProductIncome.period_type == 'monthly',
                ProductIncome.product_id == id,
                ProductIncome.record_date.like(f"%{latest_year}%")
            )).order_by(desc(ProductIncome.record_date)).limit(6).all()

            monthCount = 0
            productName = Product.query.filter(Product.id == id).first()
            
            if not productName:
                continue

            test = {
                productName.product_name: {}
            }

            total_units = 0
            total_income = 0

            # Initialize all months with zero values
            for monthName in monthNames:  
                test[productName.product_name][f'{monthName}'] = {
                    'Total unit sold': 0,
                    'Total unit income': 0.0
                }

            # Process each week's data
            for month in anItem:
                stuff = {
                    f'{monthNames[monthCount]}': {
                        'Total unit sold': month.total_units_sold or 0,
                        'Total unit income': float(month.product_specific_income or 0),
                    }
                }
                total_units += month.total_units_sold or 0
                total_income += float(month.product_specific_income or 0)
                test[productName.product_name].update(stuff)
                monthCount += 1

            # Add product totals
            test[productName.product_name]['Product Totals'] = {
                'Total unit sold': total_units,
                'Total unit income': total_income
            }

            sheetData.update(test)

        # Create initial DataFrame
        df = pd.DataFrame.from_dict(sheetData, orient='index')

        # Create a new DataFrame with better structure
        structured_df = pd.DataFrame(index=df.index)

        # Process each column (month) separately
        for column in df.columns:
            if column != 'Product Totals':
                # Extract units sold and income into separate columns with error handling
                structured_df[f'{column} - Units'] = df[column].apply(
                    lambda x: x.get('Total unit sold', 0) if isinstance(x, dict) else 0
                )
                structured_df[f'{column} - Income'] = df[column].apply(
                    lambda x: x.get('Total unit income', 0.0) if isinstance(x, dict) else 0.0
                )

        # Add product totals
        structured_df['Total Units'] = df['Product Totals'].apply(
            lambda x: x.get('Total unit sold', 0) if isinstance(x, dict) else 0
        )
        structured_df['Total Income'] = df['Product Totals'].apply(
            lambda x: x.get('Total unit income', 0.0) if isinstance(x, dict) else 0.0
        )

        # Calculate monthly totals
        monthly_totals = {}
        for column in structured_df.columns:
            if 'Units' in column or 'Income' in column:
                monthly_totals[column] = structured_df[column].sum()

        # Add monthly totals row
        structured_df.loc['Monthly Totals'] = monthly_totals

        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'monthly_sales_report_{timestamp}.xlsx'

        # Create full file path (put this in your desired directory)
        file_path = os.path.join('C:/Users/james/OneDrive/Documents/Babcock/project/FYP/Main project chapters/FYP_website/view', filename)

        # Create Excel writer object
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            # Write DataFrame to Excel
            structured_df.to_excel(writer, sheet_name='Sales Report')
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Sales Report']
            
            # Add formatting
            money_format = workbook.add_format({'num_format': '₦#,##0.00'})
            number_format = workbook.add_format({'num_format': '#,##0'})
            
            # Apply formatting to columns
            for col_num, column in enumerate(structured_df.columns):
                max_length = max(
                    structured_df[column].astype(str).apply(len).max(),
                    len(column)
                )
                worksheet.set_column(col_num + 1, col_num + 1, max_length + 2)
                
                if 'Income' in column:
                    worksheet.set_column(col_num + 1, col_num + 1, max_length + 2, money_format)
                elif 'Units' in column:
                    worksheet.set_column(col_num + 1, col_num + 1, max_length + 2, number_format)

        return jsonify({'message': f'Report generated: {filename}'}), 201
@report_route.route('/yearly')
class yearlyReport(MethodView):

    def get(self):
         # Get all product IDs from the database
        prodID = Product.query.all()
        prodID = [id.id for id in prodID]

        years = ProductIncome.query.with_entities(extract('year', ProductIncome.record_date).label('year')).distinct().all()
        years = [year[0] for year in years]
        print(years)

        # Initialize empty dictionaries to store the data
        sheetData = {}

        # Loop through each product ID
        for id in prodID:
            # Query weekly records for current product
            anItem = ProductIncome.query.filter(and_(
                ProductIncome.period_type == 'yearly',
                ProductIncome.product_id == id
            )).order_by(ProductIncome.record_date).all()

            yearCount = 0
            productName = Product.query.filter(Product.id == id).first()
            
            if not productName:
                continue

            test = {
                productName.product_name: {}
            }

            total_units = 0
            total_income = 0

            # Initialize all years with zero values
            for year in years:
                test[productName.product_name][f'{year}'] = {
                    'Total unit sold': 0,
                    'Total unit income': 0.0
                }

            # Process each year data
            for year in anItem:
                stuff = {
                    f'{years[yearCount]}': {
                        'Total unit sold': year.total_units_sold or 0,
                        'Total unit income': float(year.product_specific_income or 0),
                    }
                }
                total_units += year.total_units_sold or 0
                total_income += float(year.product_specific_income or 0)
                test[productName.product_name].update(stuff)
                yearCount += 1

            # Add product totals
            test[productName.product_name]['Product Totals'] = {
                'Total unit sold': total_units,
                'Total unit income': total_income
            }

            sheetData.update(test)

        # Create initial DataFrame
        df = pd.DataFrame.from_dict(sheetData, orient='index')

        # Create a new DataFrame with better structure
        structured_df = pd.DataFrame(index=df.index)

        # Process each column (year) separately
        for column in df.columns:
            if column != 'Product Totals':
                # Extract units sold and income into separate columns with error handling
                structured_df[f'{column} - Units'] = df[column].apply(
                    lambda x: x.get('Total unit sold', 0) if isinstance(x, dict) else 0
                )
                structured_df[f'{column} - Income'] = df[column].apply(
                    lambda x: x.get('Total unit income', 0.0) if isinstance(x, dict) else 0.0
                )

        # Add product totals
        structured_df['Total Units'] = df['Product Totals'].apply(
            lambda x: x.get('Total unit sold', 0) if isinstance(x, dict) else 0
        )
        structured_df['Total Income'] = df['Product Totals'].apply(
            lambda x: x.get('Total unit income', 0.0) if isinstance(x, dict) else 0.0
        )

        # Calculate yearly totals
        yearly_totals = {}
        for column in structured_df.columns:
            if 'Units' in column or 'Income' in column:
                yearly_totals[column] = structured_df[column].sum()

        # Add weekly totals row
        structured_df.loc['Yearly Totals'] = yearly_totals

        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'yearly_sales_report_{timestamp}.xlsx'

        # Create full file path (put this in your desired directory)
        file_path = os.path.join('C:/Users/james/OneDrive/Documents/Babcock/project/FYP/Main project chapters/FYP_website/view', filename)

        # Create Excel writer object
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            # Write DataFrame to Excel
            structured_df.to_excel(writer, sheet_name='Sales Report')
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Sales Report']
            
            # Add formatting
            money_format = workbook.add_format({'num_format': '₦#,##0.00'})
            number_format = workbook.add_format({'num_format': '#,##0'})
            
            # Apply formatting to columns
            for col_num, column in enumerate(structured_df.columns):
                max_length = max(
                    structured_df[column].astype(str).apply(len).max(),
                    len(column)
                )
                worksheet.set_column(col_num + 1, col_num + 1, max_length + 2)
                
                if 'Income' in column:
                    worksheet.set_column(col_num + 1, col_num + 1, max_length + 2, money_format)
                elif 'Units' in column:
                    worksheet.set_column(col_num + 1, col_num + 1, max_length + 2, number_format)

        return jsonify({'message': f'Report generated: {filename}'}), 201