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


invoice = Blueprint("invoice", __name__)
invoice_route = apiBlueprint('invoice_route', __name__, url_prefix='/api/invoice', description='Get the suppliers receipt')

@invoice.route("/invoice")
@manager_required
def invoice_page():
    return render_template("invoices.html")


@invoice_route.route('/all_invoice')
class allInvoice(MethodView):
    @jwt_required()
    @manager_required
    def get(self):
        invoices = Invoice.query.order_by(Invoice.id.desc()).all()
        invoices = [
            {'date': invoice.date_issued.strftime("%Y-%m-%d"),
             'name': invoice.invoice_name,
            'id': invoice.id}
        for invoice in invoices]

        return jsonify(invoices), 200

@invoice_route.route('/downInvoice')
class downInvoice(MethodView):

    @jwt_required()
    @manager_required
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