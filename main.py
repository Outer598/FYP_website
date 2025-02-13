from flask import Flask
from flask_cors import CORS
from model.db import db, ma
from view.dashboard import dashBoard, dashboard_route
from view.category import category, category_route
from view.product import product, product_route
from view.description import description, description_route
from view.report import *
from dotenv import load_dotenv, dotenv_values
import os
from flask_smorest import Api
#init app
app = Flask(__name__)

load_dotenv()
config = dotenv_values(".env")

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

#init CORS {CROSS ORIGIN RESOURCE SHARING}
CORS(app)

#init db
db.init_app(app=app)
#init ma
ma.init_app(app=app)

api = Api(app)

app.register_blueprint(dashBoard)
app.register_blueprint(category)
app.register_blueprint(product)
app.register_blueprint(description)

api.register_blueprint(dashboard_route)
api.register_blueprint(category_route)
api.register_blueprint(product_route)
api.register_blueprint(description_route)
api.register_blueprint(report_route)

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
