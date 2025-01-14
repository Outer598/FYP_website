from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from sqlalchemy import Integer, String, DECIMAL, Date, ForeignKey, extract, desc, Column
from sqlalchemy.orm import relationship


db = SQLAlchemy()
ma = Marshmallow()

class Category(db.Model):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String(50), unique=True, nullable=False)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, nullable=False)
    f_name = Column(String(50), nullable=False)
    l_name = Column(String(50), nullable=False)
    contact = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    company_name = Column(String(100))

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    amount_sold = Column(Integer, default=0)

    category = relationship('Category', cascade="all, delete")
    supplier = relationship('Supplier', cascade="all, delete")

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    current_stock_level = Column(Integer, nullable=False)
    original_stock_level = Column(Integer, nullable=False)
    reordering_threshold = Column(Integer, default=0)

    product = relationship('Product', cascade="all, delete")

class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, nullable=False)
    f_name = Column(String(50), nullable=False)
    l_name = Column(String(50), nullable=False)
    contact = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    customer_password = Column(String(100), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Integer, nullable=False)

    customer = relationship('Customer', cascade="all, delete")
    product = relationship('Product', cascade="all, delete")

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'))
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    total_amount = Column(Integer, default=0, nullable=False)
    payment_method = Column(String(50), nullable=False)

    order = relationship('Order', cascade="all, delete")
    customer = relationship('Customer', cascade="all, delete")

class ProductIncome(db.Model):
    __tablename__ = 'product_incomes'
    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    product_specific_income = Column(DECIMAL(10, 2))
    total_units_sold = Column(Integer, nullable=False)
    period_type = Column(String(50), nullable=False)
    record_date = Column(Date, nullable=False)

    product = relationship('Product', cascade="all, delete")

class Report(db.Model):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, nullable=False)
    report_name = Column(String(120), nullable=False)
    report_type = Column(String(20), nullable=False)
    product_income_id = Column(Integer, ForeignKey('product_incomes.id', ondelete='CASCADE'), nullable=False)

    product_income = relationship('ProductIncome', cascade="all, delete")

class Department(db.Model):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, nullable=False)
    department_name = Column(String(50), nullable=False)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, nullable=False)
    f_name = Column(String(50), nullable=False)
    l_name = Column(String(50), nullable=False)
    phone_no = Column(String(20), nullable=False)
    hire_date = Column(Date, nullable=False)
    email = Column(String(100), nullable=False)
    emp_password = Column(String(100), nullable=False)
    emp_position = Column(String(100))
    department_id = Column(Integer, ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    supervisor_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'))

    department = relationship('Department', cascade="all, delete")
    supervisor = relationship('Employee', remote_side=[id])

class Receipt(db.Model):
    __tablename__ = 'receipt'
    id = Column(String(10), primary_key=True, nullable=False)
    receipt_name = Column(String(50))
    date_issued = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)

    order = relationship('Order', cascade="all, delete")
    transaction = relationship('Transaction', cascade="all, delete")
    customer = relationship('Customer', cascade="all, delete")




#marshmallow chema declarations
# CategorySchema
class CategorySchema(ma.Schema):
    class Meta:
        model = Category
        load_instance = True

    id = fields.Int(dump_only=True)
    category_name = fields.Str(required=True)

# Supplier Schema
class SupplierSchema(ma.Schema):
    class Meta:
        model = Supplier
        load_instance = True

    id = fields.Int(dump_only=True)
    f_name = fields.Str(required=True)
    l_name = fields.Str(required=True)
    contact = fields.Str(required=True)
    email = fields.Str(required=True)
    company_name = fields.Str()

# Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        model = Product
        load_instance = True

    id = fields.Int(dump_only=True)
    product_name = fields.Str(required=True)
    category_id = fields.Int(required=True, load_only=True)
    supplier_id = fields.Int(required=True, load_only=True)
    price = fields.Float(required=True)
    amount_sold = fields.Int(dump_only=True)
    category = fields.Nested(CategorySchema, dump_only=True)
    supplier = fields.Nested(SupplierSchema, dump_only=True)

# Inventory Schema
class InventorySchema(ma.Schema):
    class Meta:
        model = Inventory
        load_instance = True

    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True, load_only=True)
    current_stock_level = fields.Int(required=True)
    original_stock_level = fields.Int(required=True)
    reordering_threshold = fields.Int()
    product = fields.Nested(ProductSchema, dump_only=True)

# Customer Schema
class CustomerSchema(ma.Schema):
    class Meta:
        model = Customer
        load_instance = True

    id = fields.Int(dump_only=True)
    f_name = fields.Str(required=True)
    l_name = fields.Str(required=True)
    contact = fields.Str(required=True)
    email = fields.Str(required=True)
    customer_password = fields.Str(load_only=True)

# Order Schema
class OrderSchema(ma.Schema):
    class Meta:
        model = Order
        load_instance = True

    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True, load_only=True)
    product_id = fields.Int(required=True, load_only=True)
    quantity = fields.Int(required=True)
    line_total = fields.Float()
    customer = fields.Nested(CustomerSchema, dump_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)

# Transaction Schema
class TransactionSchema(ma.Schema):
    class Meta:
        model = Transaction
        load_instance = True

    id = fields.Int(dump_only=True)
    customer_id = fields.Int(load_only=True)
    order_id = fields.Int(required=True, load_only=True)
    total_amount = fields.Float(required=True)
    payment_method = fields.Str(required=True)
    order = fields.Nested(OrderSchema, dump_only=True)
    customer = fields.Nested(CustomerSchema, dump_only=True)

# ProductIncome Schema
class ProductIncomeSchema(ma.Schema):
    class Meta:
        model = ProductIncome
        load_instance = True

    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True, load_only=True)
    product_specific_income = fields.Float()
    total_units_sold = fields.Int(required=True)
    period_type = fields.Str(required=True)
    record_date = fields.Str(required=True)
    product = fields.Nested(ProductSchema, dump_only=True)

# Report Schema
class ReportSchema(ma.Schema):
    class Meta:
        model = Report
        load_instance = True

    id = fields.Int(dump_only=True)
    report_name = fields.Str(required=True)
    report_type = fields.Str(required=True)
    product_income_id = fields.Int(required=True, load_only=True)
    product_income = fields.Nested(ProductIncomeSchema, dump_only=True)

# Department Schema
class DepartmentSchema(ma.Schema):
    class Meta:
        model = Department
        load_instance = True

    id = fields.Int(dump_only=True)
    department_name = fields.Str(required=True)

# Employee Schema
class EmployeeSchema(ma.Schema):
    class Meta:
        model = Employee
        load_instance = True

    id = fields.Int(dump_only=True)
    f_name = fields.Str(required=True)
    l_name = fields.Str(required=True)
    phone_no = fields.Str(required=True)
    hire_date = fields.Str(required=True)
    email = fields.Str(required=True)
    emp_password = fields.Str(load_only=True)
    emp_position = fields.Str()
    department_id = fields.Int(required=True, load_only=True)
    supervisor_id = fields.Int(load_only=True)
    department = fields.Nested(DepartmentSchema, dump_only=True)
    supervisor = fields.Nested(lambda: EmployeeSchema(exclude=("supervisor",)), dump_only=True)

# Receipt Schema
class ReceiptSchema(ma.Schema):
    class Meta:
        model = Receipt
        load_instance = True

    id = fields.Int(dump_only=True)
    receipt_name = fields.Str()
    date_issued = fields.Str(required=True)
    customer_id = fields.Int(required=True, load_only=True)
    order_id = fields.Int(required=True, load_only=True)
    transaction_id = fields.Int(required=True, load_only=True)
    order = fields.Nested(OrderSchema, dump_only=True)
    transaction = fields.Nested(TransactionSchema, dump_only=True)
    customer = fields.Nested(CustomerSchema, dump_only=True)
