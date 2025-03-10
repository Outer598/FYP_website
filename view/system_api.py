from flask import render_template, Blueprint, jsonify, request, current_app, send_file
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from email.mime.text import MIMEText
import smtplib
import os
import io
from dotenv import load_dotenv, dotenv_values
from datetime import datetime, timedelta
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
    

@external_api_route.route('/updateProduct')
class updateProd(MethodView):
    

    @external_api_route.response(200, "Sales processed successfully")
    @external_api_route.response(400, "Invalid input")
    @external_api_route.response(500, "Server error")
    def patch(self):
      try:
          update_data = request.get_json()
          product_ids = update_data.get('product_ids', [])
          amounts_sold = update_data.get('amount_being_sold', [])
          email = update_data.get('email')
          
          # Validate input data
          if len(product_ids) != len(amounts_sold):
              return jsonify({'message': 'Error: product_ids and amount_being_sold must have same length'}), 400
          
          # Check if it's a new day first, to reset counters if necessary
          new_day_happened = self.newDay()
          
          # Check for other time period changes and create/update aggregation records
          self.update_if_next_week()
          self.update_if_next_month()
          self.update_if_next_year()
          
          # Make sure all products have daily records
          self.checkUpdate(product_ids)
          
          # Now process the actual sales
          self.process_sales(product_ids, amounts_sold)

          if email is not None and email != '':
              self.send_review(email=email)
          
          return jsonify({'message': "Sales processed successfully"}), 200
      
      except Exception as e:
          return jsonify({'message': 'Error processing request', 'error': str(e)}), 500
    
    def process_sales(self, product_ids, amounts_sold):
      try:
          for i, product_id in enumerate(product_ids):
              amount_sold = amounts_sold[i]
              
              # Skip if no units sold
              if amount_sold <= 0:
                  continue
                  
              # Get product information
              product = Product.query.get(product_id)
              if not product:
                  raise Exception(f'Product with ID {product_id} not found')
              
              # Get product price
              product_price = float(product.price)
              
              # Calculate income from this sale
              sale_income = product_price * amount_sold
              
              # Update inventory
              inventory = Inventory.query.filter_by(product_id=product_id).first()
              if not inventory:
                  raise Exception(f'No inventory found for product {product_id}')
              
              # Check if there's enough stock
              if inventory.current_stock_level < amount_sold:
                  raise Exception(f'Not enough stock for product {product_id}. Available: {inventory.current_stock_level}, Requested: {amount_sold}')
              
              # Update inventory
              inventory.current_stock_level -= amount_sold
              db.session.add(inventory)
              
              # Update daily product income (we know it exists because of checkUpdate)
              daily_income = ProductIncome.query.filter(and_(
                  ProductIncome.product_id == product_id,
                  ProductIncome.period_type == 'daily'
              )).first()
              
              # Update the record
              daily_income.product_specific_income = float(daily_income.product_specific_income) + sale_income
              daily_income.total_units_sold += amount_sold
              db.session.add(daily_income)
          
          # Commit all changes at once
          db.session.commit()
          
      except Exception as e:
          db.session.rollback()
          raise Exception(f'Error processing sales: {str(e)}')
        
    def checkUpdate(self, datas: list):
      for id in datas:
        # Use .first() to get the first result or None
        daily_exist = ProductIncome.query.filter(and_(
            ProductIncome.product_id == id,
            ProductIncome.period_type == 'daily'
        )).first()
        
        if daily_exist is None:
          try:
            new_product_income = ProductIncome(
              product_id = id,
              product_specific_income = float(0),
              total_units_sold = 0,
              period_type = 'daily',
              record_date = datetime.now()
            )
            db.session.add(new_product_income)
            db.session.commit()
          except Exception as e:
            db.session.rollback()
            raise Exception(f'Error adding product: {str(e)}')

    # DAILY TO WEEKLY AGGREGATION
    def newDay(self):
        now = datetime.today()
        latest_date = db.session.query(func.max(ProductIncome.record_date)).scalar()
        
        # If there are no records yet or it's a new day
        if latest_date is None or now.date() > latest_date.date():
            # Get all daily records
            daily_records = ProductIncome.query.filter(ProductIncome.period_type == 'daily').all()
            
            try:
                # Before resetting, aggregate daily data into weekly records
                self.aggregate_daily_to_weekly(daily_records)
                
                for record in daily_records:
                    # Reset values for the new day
                    record.product_specific_income = float(0)
                    record.total_units_sold = 0
                    record.record_date = now
                    db.session.add(record)
                
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise Exception(f'Error updating for new day: {str(e)}')
        
        return False

    def aggregate_daily_to_weekly(self, daily_records):
        """Aggregate daily data into weekly records without requiring start of week."""
        now = datetime.now()
        current_week = now.isocalendar()[1]
        current_year = now.year
        
        # Group daily records by product_id
        product_records = {}
        for record in daily_records:
            if record.product_id not in product_records:
                product_records[record.product_id] = []
            product_records[record.product_id].append(record)
        
        # For each product, aggregate daily data into weekly record
        for product_id, records in product_records.items():
            # Find or create weekly record for this product
            weekly_record = ProductIncome.query.filter(and_(
                ProductIncome.product_id == product_id,
                ProductIncome.period_type == 'weekly',
                extract('week', ProductIncome.record_date) == current_week,
                extract('year', ProductIncome.record_date) == current_year
            )).first()
            
            # If no weekly record exists for current week, create one
            if weekly_record is None:
                weekly_record = ProductIncome(
                    product_id=product_id,
                    product_specific_income=0,
                    total_units_sold=0,
                    period_type='weekly',
                    record_date=now
                )
                db.session.add(weekly_record)
            
            # Calculate totals from daily records
            daily_income = sum(float(record.product_specific_income) for record in records)
            daily_units = sum(record.total_units_sold for record in records)
            
            # Add to the weekly record (accumulate)
            weekly_record.product_specific_income = float(weekly_record.product_specific_income) + daily_income
            weekly_record.total_units_sold += daily_units
            
            print(f"Updated weekly record for product {product_id}: added ${daily_income}, {daily_units} units")
    
    # WEEKLY TO MONTHLY AGGREGATION
    def update_if_next_week(self):
        """Create new weekly records at the start of each week and also aggregate weekly data into monthly records."""
        now = datetime.now()
        # Check if today is the first day of the week (Monday)
        is_start_of_week = now.weekday() == 6
        
        if not is_start_of_week:
            return False  # Not the start of a week
            
        # Get last week's data for aggregation to monthly
        self.aggregate_weekly_to_monthly()
        
        # No reset of weekly records - they continue to accumulate for the current week
        # Remove the reset code that was here before
        
        db.session.commit()
        return True
    
    def aggregate_weekly_to_monthly(self):
        """Aggregate weekly data into monthly records."""
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        current_week = now.isocalendar()[1]
        
        # Get all products with weekly records
        products = db.session.query(ProductIncome.product_id).filter(
            ProductIncome.period_type == 'weekly'
        ).distinct().all()
        
        for product_tuple in products:
            product_id = product_tuple[0]
            
            # Get only the current week's records for this product
            weekly_records = ProductIncome.query.filter(and_(
                ProductIncome.product_id == product_id,
                ProductIncome.period_type == 'weekly',
                extract('week', ProductIncome.record_date) == current_week,
                extract('year', ProductIncome.record_date) == current_year
            )).all()
            
            if not weekly_records:
                continue
                
            # Find or create monthly record for this product
            monthly_record = ProductIncome.query.filter(and_(
                ProductIncome.product_id == product_id,
                ProductIncome.period_type == 'monthly',
                extract('month', ProductIncome.record_date) == current_month,
                extract('year', ProductIncome.record_date) == current_year
            )).first()
            
            # If no monthly record exists for current month, create one
            if monthly_record is None:
                monthly_record = ProductIncome(
                    product_id=product_id,
                    product_specific_income=0,
                    total_units_sold=0,
                    period_type='monthly',
                    record_date=now
                )
                db.session.add(monthly_record)
            
            # Calculate totals from weekly records (only current week)
            weekly_income = sum(float(record.product_specific_income) for record in weekly_records)
            weekly_units = sum(record.total_units_sold for record in weekly_records)
            
            # Add to the monthly record (accumulate)
            monthly_record.product_specific_income = float(monthly_record.product_specific_income) + weekly_income
            monthly_record.total_units_sold += weekly_units
            
            print(f"Updated monthly record for product {product_id}: added ${weekly_income}, {weekly_units} units")
    
    # MONTHLY TO YEARLY AGGREGATION
    def update_if_next_month(self):
        """Handle the transition to a new month and aggregate monthly data into yearly records."""
        now = datetime.now()
        # Check if today is the first day of the month
        is_start_of_month = now.day == 1
        
        if not is_start_of_month:
            return False  # Not the start of a month
        
        # Aggregate monthly data into yearly before resetting
        self.aggregate_monthly_to_yearly()
        
        # No reset of monthly records - they continue to accumulate for the current month
        # Remove the reset code that was here before
        
        db.session.commit()
        return True
    
    def aggregate_monthly_to_yearly(self):
        """Aggregate monthly data into yearly records."""
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Get all products with monthly records
        products = db.session.query(ProductIncome.product_id).filter(
            ProductIncome.period_type == 'monthly'
        ).distinct().all()
        
        for product_tuple in products:
            product_id = product_tuple[0]
            
            # Get only the current month's records for this product
            monthly_records = ProductIncome.query.filter(and_(
                ProductIncome.product_id == product_id,
                ProductIncome.period_type == 'monthly',
                extract('month', ProductIncome.record_date) == current_month,
                extract('year', ProductIncome.record_date) == current_year
            )).all()
            
            if not monthly_records:
                continue
                
            # Find or create yearly record for this product
            yearly_record = ProductIncome.query.filter(and_(
                ProductIncome.product_id == product_id,
                ProductIncome.period_type == 'yearly',
                extract('year', ProductIncome.record_date) == current_year
            )).first()
            
            # If no yearly record exists for current year, create one
            if yearly_record is None:
                yearly_record = ProductIncome(
                    product_id=product_id,
                    product_specific_income=0,
                    total_units_sold=0,
                    period_type='yearly',
                    record_date=now
                )
                db.session.add(yearly_record)
            
            # Calculate totals from monthly records (only current month)
            monthly_income = sum(float(record.product_specific_income) for record in monthly_records)
            monthly_units = sum(record.total_units_sold for record in monthly_records)
            
            # Add to the yearly record (accumulate)
            yearly_record.product_specific_income = float(yearly_record.product_specific_income) + monthly_income
            yearly_record.total_units_sold += monthly_units
            
            print(f"Updated yearly record for product {product_id}: added ${monthly_income}, {monthly_units} units")
    
    # YEARLY UPDATING (NOT RESETTING)
    def update_if_next_year(self):
        """Handle the transition to a new year without resetting yearly records."""
        now = datetime.now()
        # Check if today is the first day of the year
        is_start_of_year = now.day == 1 and now.month == 1
        
        if not is_start_of_year:
            return False  # Not the start of a year
        
        # No reset of yearly records - they continue to accumulate
        # Remove the reset code that was here before
        
        db.session.commit()
        return True
    

    def send_review(self, email):
        subject = 'We like your feed back'
        body = f'''Dear Customer,
        
Good day thank you for shopping at Babcock sSuperStore we value your feedback and if it not too much to ask we would like for you to take a few moment of your time and help us write a review which would help us in return to improve our services to not only you but to our other customers

website link:  https://3b73-102-88-108-181.ngrok-free.app

Thank you so much for taken a moment of your time to consider our reuqest.

Your Faithfully,
Babcock SuperStore team

Note: this is a no-reply email so messages sent won't be recieved on this email. 
        '''
        sender = os.getenv("myemailaddress")
        recipient = email
        app_password = os.getenv("myemailapppassword")

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_sever:
            smtp_sever.login(sender, app_password)
            smtp_sever.sendmail(sender, recipient, msg.as_string())
        return True