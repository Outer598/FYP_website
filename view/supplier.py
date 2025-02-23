from flask import render_template, Blueprint, jsonify, request, current_app
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from view.madepass import SecurePasswordGenerator
from flask_mail import Mail, Message
from email.mime.text import MIMEText
import smtplib


supplier = Blueprint("supplier", __name__)
supplier_route = apiBlueprint('supplier_route', __name__, url_prefix='/api/supplier', description='For supplier')

@supplier.route("/supplier")
def suppliers():
    return render_template("supplier.html")



@supplier_route.route('/all_supplier')
class allSuppliers(MethodView):

    def get(self):
        all_supplier = Supplier.query.all()
        all_supplier = [{'id': supplier.id, 'name': supplier.s_name} for supplier in all_supplier]
        
        for i in all_supplier:
            products = Product.query.filter(Product.supplier_id == i['id']).all()
            i.update({'assignedProduct': len(products)})

        return jsonify(all_supplier), 200
    
    def post(self):
        data = request.get_json()
    
        generator = SecurePasswordGenerator(length=16, use_digits=True, use_special_chars=True)

        suppliers = Supplier.query.all()
        supplierEmails = [supplierEmail.email for supplierEmail in suppliers]
        
        supplierPhoneNos = [supplierphoneno.contact for supplierphoneno in suppliers]

        if 'suppliersEmail' not in data or 'suppliersPhoneNo' not in data:
            return jsonify({"message": "Missing required fields"}), 400  # Bad Request

        if data['suppliersEmail'] in supplierEmails or data['suppliersPhoneNo'] in supplierPhoneNos:
            return jsonify({"message": "Supplier with Email or Phone No already exists"}), 409  # Conflict

        data.update({'suppliersPassword': generator.generate_password()})
        
        if any(value == '' for value in data.values()):
            return {'message': "Required fields cannot be emppty"}, 500

        subject = 'Welcome to Babcock suppliers'
        body = f'''Dear {data["suppliersName"].title()},
        Welcome to babcock suppliers teams see below the password and email you wil use to be able tpo logon to our platform for invoice and reciept upload and download respectively.
        Email: {data["suppliersEmail"]}
        Password: {data["suppliersPassword"]}
        website link:  https://3b73-102-88-108-181.ngrok-free.app

        Note: this is a no-reply email so messages sent wont be recieved on this email. 
        Thank you and welcome onboard'''
        sender = 'no.reply.babcock@gmail.com'
        recipient = data["suppliersEmail"]
        app_password = 'jbxcvtllscshtimr'

        try:
            newSupplier = Supplier(s_name=data['suppliersName'], 
                                   contact=data['suppliersPhoneNo'], 
                                   email=data['suppliersEmail'], 
                                   company_name=data['suppliersCompaniesName'])
            newSupplier.password = data['suppliersPassword']
            db.session.add(newSupplier)
            db.session.commit()
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_sever:
                smtp_sever.login(sender, app_password)
                smtp_sever.sendmail(sender, recipient, msg.as_string())
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return jsonify({'message': 'Error sending welcome email', 'error': str(e)}), 500

        return jsonify({'message': 'supplier succesfully created'}), 202
    

@supplier_route.route('/all_supplier/<int:id>')
class delSupplier(MethodView):

    def delete(self, id):
        supplier = Supplier.query.filter(Supplier.id == id).first()

        supplier_prod = Supplier.query.join(Product, Supplier.id == Product.supplier_id).filter(Product.supplier_id == id).all()

        if supplier_prod:
            return jsonify({'message': "Product assigned to Supplier."}), 500

        if not supplier:
            return jsonify({'message': 'Supplier does not exist'}), 404
        
        try: 
            db.session.delete(supplier)
            db.session.commit()
            return jsonify({'message': 'Supplier Successfully deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error deleting Supplier', 'error': str(e)}), 500
        
