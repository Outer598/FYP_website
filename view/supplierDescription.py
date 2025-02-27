from flask import render_template, Blueprint, jsonify, request, current_app, send_file
import mimetypes
from werkzeug.utils import secure_filename
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from view.madepass import SecurePasswordGenerator
from flask_mail import Mail, Message
from email.mime.text import MIMEText
import smtplib
import os
import io
from dotenv import load_dotenv, dotenv_values
from datetime import datetime

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




@supplierDes_route.route('/getReceipt')
class getReceipt(MethodView):
    
        def get(self):
            data = request.args.get('id')

            receipt = Receipt.query.join(Supplier, Receipt.supplier_id == Supplier.id).filter(Receipt.supplier_id == data).all()
            all_receipts = []
            for i in receipt:
                all_receipts.append({
                    'id': i.id,
                    'name': i.receipt_name,
                    'date': i.date_issued,
                })
            return jsonify(all_receipts), 200
        
        def post(self):
            supplier_id = request.args.get('id')
            file_name = request.form.get('file_name')
            file = request.files.get('file')  # Use .get() to avoid KeyError

            # Check if the supplier has products assigned
            supplier_product = Supplier.query.join(Product, Supplier.id == Product.supplier_id).filter(Supplier.id == supplier_id).all()
            if not supplier_product:
                return jsonify({"message": "Can't Upload File due to lack of product being assigned to supplier"}), 404

            # Ensure required fields are provided
            if not supplier_id or not file_name or not file:
                return jsonify({"message": "Missing required fields"}), 400

            try:
                # Read the binary content before committing
                file_data = file.read()

                # Get MIME type from filename
                mime_type, _ = mimetypes.guess_type(file.filename)

                # Ensure a secure filename
                safe_filename = secure_filename(file_name)

                # Save receipt with actual binary data
                receipt = Receipt(
                    receipt_name=safe_filename,
                    receipt_data=file_data,  # Store actual binary content
                    supplier_id=supplier_id,
                    date_issued=datetime.now().strftime('%Y-%m-%d')
                )

                db.session.add(receipt)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Unable to add receipt', 'error': str(e)}), 500

            return jsonify({'message': 'Receipt added successfully'}), 201

        

@supplierDes_route.route('/downReceipt')
class downReceipt(MethodView):
    def get(self):
        id = request.args.get('id')
        receipt = Receipt.query.filter_by(id=id).first()

        if not receipt or not receipt.receipt_data:
            return jsonify({"error": "File not found or file data is empty"}), 404

        try:
            # Read file as stored
            file_data = io.BytesIO(receipt.receipt_data)
            file_data.seek(0)

            # Get filename and attempt MIME type detection
            filename = receipt.receipt_name
            mime_type, _ = mimetypes.guess_type(filename)

            # Extract file extension safely
            file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

            # Read first 32 bytes for file signature checking
            file_signature = receipt.receipt_data[:32]

            # Dictionary mapping file signatures to MIME types
            magic_signatures = {
                b'%PDF': 'application/pdf',
                b'\x89PNG\r\n\x1a\n': 'image/png',
                b'\xff\xd8\xff': 'image/jpeg',
                b'II*\x00': 'image/tiff',  # TIFF (little-endian)
                b'MM\x00*': 'image/tiff',  # TIFF (big-endian)
                b'\xd0\xcf\x11\xe0': 'application/msword',  # DOC (old format)
                b'PK\x03\x04': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # DOCX
            }

            # Check file signature
            for sig, detected_mime in magic_signatures.items():
                if file_signature.startswith(sig):
                    mime_type = detected_mime
                    break

            # Fallback to extension-based MIME type if signature not detected
            if not mime_type:
                ext_mime_map = {
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'doc': 'application/msword',
                    'txt': 'text/plain',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'tif': 'image/tiff',
                    'tiff': 'image/tiff'
                }
                mime_type = ext_mime_map.get(file_ext, 'application/octet-stream')

            # Ensure a safe filename for downloading
            safe_filename = secure_filename(filename) if filename else f"downloaded_file.{file_ext}"

            # Send file without any transformation
            response = send_file(
                file_data,
                mimetype=mime_type,
                as_attachment=True,
                download_name=safe_filename,
                conditional=False
            )

            # Ensure correct Content-Type
            response.headers["Content-Type"] = mime_type
            response.headers["Content-Disposition"] = f'attachment; filename="{safe_filename}"'

            return response

        except Exception as e:
            current_app.logger.error(f"Error sending file: {str(e)}")
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
        

    def delete(self):
        try:
            id = request.args.get('id')
            receipt = Receipt.query.filter(Receipt.id == id).first()
            print(receipt)
    
            if not receipt:
                return jsonify({"error": "File not found"}), 404  # JSON if no file found
            
            db.session.delete(receipt)
            db.session.commit()
            return jsonify({"message":"Receipt Deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'error deleting receipt', 'error': str(e)}), 500