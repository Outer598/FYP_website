from flask import render_template, Blueprint, jsonify, request, current_app
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from model.db import *
from view.madepass import SecurePasswordGenerator
from flask_mail import Mail, Message
from email.mime.text import MIMEText
import smtplib


supplierDes = Blueprint("supplierDescription", __name__)
supplierDes_route = apiBlueprint('supplierDescription_route', __name__, url_prefix='/api/supplierDescription', description='For supplier')

@supplierDes.route("/supplier/description")
def supplierDescription():
    return render_template("s_description.html")