from flask import render_template, Blueprint, jsonify, request, current_app
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from view.madepass import SecurePasswordGenerator
from flask_mail import Mail, Message
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values(".env")

supplierDes = Blueprint("supplierDescription", __name__)
supplierDes_route = apiBlueprint('supplierDescription_route', __name__, url_prefix='/api/supplierDescription', description='For supplier')

@supplierDes.route("/supplier/description")
def supplierDescription():
    return render_template("s_description.html")


@supplierDes_route.route('/info')
class supplierInfo(MethodView):

    def get(self):
        data = request.args.get('id')

        supplier_info = Supplier.query.filter(Supplier.id == data).first()

        return jsonify({
            'name': supplier_info.s_name,
            'email': supplier_info.email,
            'phone': supplier_info.contact,
            'company': supplier_info.company_name,
        }), 200


@supplierDes_route.route('/product')
class supplierProduct(MethodView):

    def get(self):
        data = request.args.get('id')

        supplier_product = Product.query.join(Supplier, Product.supplier_id == Supplier.id).filter(Product.supplier_id == data).all()

        product_list = []
        for i in supplier_product:
            amount_remain = Product.query.join(Inventory, Product.id == Inventory.product_id).filter(Product.id == i.id).first()
            product_list.append({
                'id': i.id,
                'name': i.product_name,
                'amount_remain': amount_remain.inventory.current_stock_level,
            })
        return jsonify(product_list), 200

@supplierDes_route.route('/mail')
class mailSupplier(MethodView):

    def post(self):
        data = request.get_json()
        print(data)
        supplier_id = request.args.get('id')
        product_id = request.args.get('product_id')

        supplier_email = Supplier.query.filter(Supplier.id == supplier_id).first()
        product_name = Product.query.filter(Product.id == product_id).first()

        subject = f'Supply Needed for {product_name.product_name}'
        body = f'''Dear {supplier_email.s_name.title()},

Hope your day is going well.

We would like to inform you that we are in need of more {product_name.product_name} we need about {data['amount']}.

We would really appreciate it if you could deliver it to us as soon as possible.

Yours Sincerely,
Babcock SuperStore Manager       

Note: this is a no-reply email so messages sent won't be recieved on this email. 
'''
        sender = os.getenv("myemailaddress")
        recipient = supplier_email.email
        app_password = os.getenv("myemailapppassword")

        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_sever:
                smtp_sever.login(sender, app_password)
                smtp_sever.sendmail(sender, recipient, msg.as_string())
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return jsonify({'message': 'Error sending email', 'error': str(e)}), 500

        return jsonify({'message': 'Mail sent succesfully'}), 202

@supplierDes_route.route('/update')
class sdesUpdate(MethodView):

    def patch(self):
        supId = request.args.get('id')
        print(supId)
        data = request.get_json()
        print(data)

        suppliers = Supplier.query.all()
        supplierEmails = [supplierEmail.email for supplierEmail in suppliers]
        
        supplierPhoneNos = [supplierphoneno.contact for supplierphoneno in suppliers]


        supplier = Supplier.query.filter(Supplier.id == supId).first()
        for key, value in data.items():
            if value == '':
                return {'message': "Field cannot be empty"}, 400
            
        
        if 'email' in data and 'contact' in data:
            if data['email'] in supplierEmails or data['contact'] in supplierPhoneNos:
                return jsonify({"message": "Supplier with Email or Phone-No already exists"}), 409  # Conflict

        
        try:
            for key, value in data.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)
        
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'Unable to update item', 'error': str(e)}, 404

        return {'message': 'Item updated Successfully'}, 200
