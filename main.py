from flask import Flask, render_template
from flask_cors import CORS
from flask_migrate import Migrate
from model.db import *
from view.dashboard import dashBoard, dashboard_route
from view.category import category, category_route
from view.product import product, product_route
from view.description import description, description_route
from view.report import report, report_route
from view.supplier import supplier, supplier_route
from view.supplierDescription import supplierDes, supplierDes_route
from view.login import login_manager, auth_bp, login_page
from view.supplier_receipt import supplier_receipt, supplier_receipt_route
from dotenv import load_dotenv, dotenv_values
import os
from flask_smorest import Api
from datetime import timedelta


def insert_users():
    users = [
        {"u_name": "John Doe", "phone_no": "+1-555-0001", "hire_date": "2023-05-10", "email": "john.doe@example.com", "password": "securepass123"},
        {"u_name": "Jane Smith", "phone_no": "+1-555-0002", "hire_date": "2022-08-15", "email": "jane.smith@example.com", "password": "myp@ssw0rd"},
        {"u_name": "Michael Brown", "phone_no": "+1-555-0003", "hire_date": "2021-11-20", "email": "michael.b@example.com", "password": "Pa$$w0rd!"},
    ]

    for data in users:
        user = User(
            u_name=data["u_name"],
            phone_no=data["phone_no"],
            hire_date=data["hire_date"],
            email=data["email"]
        )
        user.password = data["password"]  # This will use the password property setter
        db.session.add(user)

    db.session.commit()
    print("Users inserted successfully!")


def insert_suppliers():
    suppliers = [
        {"s_name": "Fisayo Aasa", "contact": "+2347014180591", "email": "fisayoaasa@gmail.com", "company_name": "Global Brands Distribution", "password": "12345"},
        {"s_name": "Sarah Johnson", "contact": "+1-555-0102", "email": "sarah.j@worldwideretail.com", "company_name": "Worldwide Retail Solutions", "password": "w&*OxJKKro^`"},
        {"s_name": "Michael Brown", "contact": "+1-555-0103", "email": "michael.b@supremegoods.com", "company_name": "Supreme Goods Co.", "password": "y3o>865Y|DmT"},
        {"s_name": "Emily Davis", "contact": "+1-555-0104", "email": "emily.d@universalmerch.com", "company_name": "Universal Merchandise", "password": "3Sa#a5u7*UXv"},
        {"s_name": "David Wilson", "contact": "+1-555-0105", "email": "david.w@primeproducts.com", "company_name": "Prime Products International", "password": "4<Lqh&-vy9))"},
        {"s_name": "Lisa Anderson", "contact": "+1-555-0106", "email": "lisa.a@elitetraders.com", "company_name": "Elite Traders LLC", "password": "^9O=u19{@\\D)"},
        {"s_name": "James Taylor", "contact": "+1-555-0107", "email": "james.t@toptierdist.com", "company_name": "Top Tier Distributors", "password": "b?Hp2KNCQ-|k"},
        {"s_name": "Jennifer Thomas", "contact": "+1-555-0108", "email": "jennifer.t@qualitygoods.com", "company_name": "Quality Goods Corp", "password": "wmdz^O1{Y}5f"},
        {"s_name": "Robert Martinez", "contact": "+1-555-0109", "email": "robert.m@premiumsupply.com", "company_name": "Premium Supply Chain", "password": 'XaSy2"/:Jr+H'},
        {"s_name": "Maria Garcia", "contact": "+1-555-0110", "email": "maria.g@megamarket.com", "company_name": "Mega Market Solutions", "password": "Q1+uGI$8n9<%"}
    ]

    for data in suppliers:
        supplier = Supplier(
            s_name=data["s_name"],
            contact=data["contact"],
            email=data["email"],
            company_name=data["company_name"]
        )
        supplier.password = data["password"]  # This will use the password property setter
        db.session.add(supplier)

    db.session.commit()
    print("Suppliers inserted successfully!")

#init app
app = Flask(__name__)

load_dotenv()
config = dotenv_values(".env")

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or os.urandom(24)

class Apiconfig:
    API_TITLE = 'Sales Analyzer'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_URL_PREFIX = '/api'
    OPENAPI_SWAGGER_UI_PATH = '/docs'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

app.config.from_object(Apiconfig)

#database init
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("myDatabaseUsername")}:{os.getenv("myDatabasePassword")}@{os.getenv("myDatabaseHost")}/{os.getenv("myDatabaseName")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = os.getenv("JWT_KEY")
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)


#init db
db.init_app(app=app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

migrate = Migrate(app, db)

api = Api(app)
login_manager.init_app(app)


app.register_blueprint(login_page)
app.register_blueprint(auth_bp)
app.register_blueprint(dashBoard)
app.register_blueprint(category)
app.register_blueprint(product)
app.register_blueprint(description)
app.register_blueprint(report)
app.register_blueprint(supplier)
app.register_blueprint(supplierDes)
app.register_blueprint(supplier_receipt)

# api.register_blueprint(auth_bp)
api.register_blueprint(dashboard_route)
api.register_blueprint(category_route)
api.register_blueprint(product_route)
api.register_blueprint(description_route)
api.register_blueprint(report_route)
api.register_blueprint(supplier_route)
api.register_blueprint(supplierDes_route)
api.register_blueprint(supplier_receipt_route)


# with app.app_context():
#     db.create_all()

#     insert_users()
#     insert_suppliers()

if __name__ == "__main__":
    app.run(debug=True)
