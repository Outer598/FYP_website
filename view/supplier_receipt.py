from flask import render_template, Blueprint, jsonify, request, current_app, send_file
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
from view.login_new import manager_required, supplier_required, session
import mimetypes
from werkzeug.utils import secure_filename
import io


supplier_receipt = Blueprint("supplier_receipt", __name__)
supplier_receipt_route = apiBlueprint('supplier_receipt_route', __name__, url_prefix='/api/receipt', description='Get the suppliers receipt')

@supplier_receipt.route("/receipt")
@supplier_required
def receipt():
    return render_template("receipt.html")


@supplier_receipt_route.route('/receipt')
class getInvoices(MethodView):
    # Add the jwt_required decorator here
    @jwt_required()
    @supplier_required
    def get(self):
        claims = get_jwt()
        user_type = claims.get('user_type')

        to_return_data = []
        if user_type == 'supplier':
            current_user_id = claims.get("supplier_id")  # Changed from "id" to "supplier_id" based on your login_new.py
            receipt_datas = Receipt.query.filter(Receipt.supplier_id == current_user_id).all()
            to_return_data = [ {
                'id': receipt_data.id,
                'name': receipt_data.receipt_name,
                'supplier_id': receipt_data.supplier_id,
                'date': receipt_data.date_issued.strftime("%Y-%m-%d")
            } for receipt_data in receipt_datas]

        return jsonify(to_return_data), 200

@supplier_receipt_route.route('/invoice')
class getInvoices(MethodView):
    # Add the jwt_required decorator here
    @jwt_required()
    @supplier_required
    def get(self):
        claims = get_jwt()
        user_type = claims.get('user_type')

        to_return_data = []
        if user_type == 'supplier':
            current_user_id = claims.get("supplier_id")  # Changed from "id" to "supplier_id" based on your login_new.py
            invoice_datas = Invoice.query.filter(Invoice.supplier_id == current_user_id).all()
            to_return_data = [ {
                'id': invoice_data.id,
                'name': invoice_data.invoice_name,
                'supplier_id': invoice_data.supplier_id,
                'date': invoice_data.date_issued.strftime("%Y-%m-%d")
            } for invoice_data in invoice_datas]

        return jsonify(to_return_data), 200
    
@supplier_receipt_route.route('/upinvoice')
class UpInvoice(MethodView):
    @jwt_required()
    @supplier_required
    def post(self):
        claims = get_jwt()
        supplier_id = claims.get('supplier_id')
        print("=== DEBUGGING REQUEST ===")
        print("Content-Type:", request.content_type)
        print("Args:", request.args)
        print("Form Data:", request.form)
        print("Files:", request.files)
        print("========================")
        
        # Check for required parameters
        if not supplier_id:
            return jsonify({"message": "Missing supplier ID"}), 400
            
        # Access form data and files
        file_name = request.form.get('file_name')
        file = request.files.get('file')
        
        if not file_name or not file:
            return jsonify({"message": "Missing file name or file"}), 400

        # Check if the supplier has products assigned
        supplier_product = Supplier.query.join(Product, Supplier.id == Product.supplier_id).filter(Supplier.id == supplier_id).all()
        if not supplier_product:
            return jsonify({"message": "Can't Upload File due to lack of product being assigned to supplier"}), 404

        try:
            # Read the binary content before committing
            file_data = file.read()

            # Get MIME type from filename
            mime_type, _ = mimetypes.guess_type(file.filename)

            # Ensure a secure filename
            safe_filename = secure_filename(file_name)

            # Save receipt with actual binary data
            newinvoice = Invoice(
                invoice_name=safe_filename,
                invoice_data=file_data,  # Store actual binary content
                supplier_id=supplier_id,
                date_issued=datetime.now().strftime('%Y-%m-%d')
            )

            db.session.add(newinvoice)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Unable to add Invoice', 'error': str(e)}), 500

        return jsonify({'message': 'Invoice added successfully'}), 201

@supplier_receipt_route.route('/downInvoice')
class downInvoice(MethodView):

    @jwt_required()
    @supplier_required
    def get(self):
        id = request.args.get('id')
        invoice = Invoice.query.filter_by(id=id).first()

        if not invoice or not invoice.invoice_data:
            return jsonify({"error": "File not found or file data is empty"}), 404

        try:
            # Read file as stored
            file_data = io.BytesIO(invoice.invoice_data)
            file_data.seek(0)

            # Get filename and attempt MIME type detection
            filename = invoice.invoice_name
            mime_type, _ = mimetypes.guess_type(filename)

            # Extract file extension safely
            file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

            # Read first 32 bytes for file signature checking
            file_signature = invoice.invoice_data[:32]

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
        
    @jwt_required()
    @supplier_required
    def delete(self):
        id = request.args.get('id')
        try:
            invoice = Invoice.query.filter(Invoice.id == id).first()
            print(invoice)
    
            if not invoice:
                return jsonify({"error": "File not found"}), 404  # JSON if no file found
            
            db.session.delete(invoice)
            db.session.commit()
            return jsonify({"message":"Invoice Deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'error deleting Invoice', 'error': str(e)}), 500

@supplier_receipt_route.route('/downReceipt')
class downReceipt(MethodView):

    @jwt_required()
    @supplier_required
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