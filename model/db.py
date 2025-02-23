from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text,DECIMAL, Date, DateTime, ForeignKey, extract, desc, Column, and_, func, LargeBinary, text
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String(50), unique=True, nullable=False)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, nullable=False)
    s_name = Column(String(50), nullable=False)
    contact = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    company_name = Column(String(100))
    p_picture = Column(LargeBinary, nullable=True)
    l_password = Column(String(255), nullable=False)  # Store hashed password

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.l_password = generate_password_hash(password)  # Set l_password directly

    def verify_password(self, password):
        return check_password_hash(self.l_password, password)  # Use l_password here

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    category = relationship('Category', backref=db.backref('products', cascade='all, delete-orphan'))
    supplier = relationship('Supplier', backref=db.backref('products', cascade='all, delete-orphan'))

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    current_stock_level = Column(Integer, nullable=False)
    original_stock_level = Column(Integer, nullable=False)
    reordering_threshold = Column(Integer, default=0)
    
    product = relationship('Product', backref=db.backref('inventory', cascade='all, delete-orphan', uselist=False))

class ProductIncome(db.Model):
    __tablename__ = 'product_incomes'
    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product_specific_income = Column(DECIMAL(10, 2))
    total_units_sold = Column(Integer, nullable=False)
    period_type = Column(String(50), nullable=False)
    record_date = Column(DateTime, nullable=False)

    product = relationship('Product', cascade=None)

class Report(db.Model):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, nullable=False)
    report_name = Column(String(120), nullable=False)
    report_data = Column(LargeBinary, nullable=False)
    date_issued = Column(DateTime, nullable=False)

class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False)
    u_name = Column(String(50), nullable=False)
    phone_no = Column(String(20), nullable=False, unique=True)
    hire_date = Column(Date, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    p_picture = Column(LargeBinary, nullable=True)
    l_password = Column(String(255), nullable=False)  # Store hashed password

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.l_password = generate_password_hash(password)  # Set l_password directly

    def verify_password(self, password):
        return check_password_hash(self.l_password, password)  # Use l_password here

    
class Receipt(db.Model):
    __tablename__ = 'receipt'
    id = Column(Integer, primary_key=True, nullable=False)
    receipt_name = Column(String(50), nullable=False)
    receipt_data = Column(LargeBinary, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    date_issued = Column(DateTime, nullable=False)

    supplier = relationship('Supplier', backref=db.backref('receipt', cascade='all, delete-orphan'))

class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True, nullable=False)
    invoice_name = Column(String(50), nullable=False)
    invoice_data = Column(LargeBinary, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    date_issued = Column(DateTime, nullable=False)
    supplier = relationship('Supplier', backref=db.backref('invoice', cascade='all, delete-orphan'))

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = Column(String(10), primary_key=True, nullable=False)
    feedback_name = Column(String(50), nullable=False)
    feedbac_data = Column(Text, nullable=False)
    date_submitted = Column(DateTime, nullable=False)