from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Users (Admin/Cashier)
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed
    role = db.Column(db.String(20), nullable=False)  # admin or cashier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Categories
class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

# Products
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='pcs')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Transactions (Sales)
class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    payment_method = db.Column(db.String(50))
    total_amount = db.Column(db.Float)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='transactions')   # Link to User
    details = db.relationship('TransactionDetail', backref='transaction', lazy=True)
    payments = db.relationship('Payment', backref='transaction', lazy=True)
    

# Transaction details (line items)
class TransactionDetail(db.Model):
    detail_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    subtotal = db.Column(db.Float)

# Payments
class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    method = db.Column(db.String(50))
    amount = db.Column(db.Float)

# Inventory logs
class InventoryLog(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    change_type = db.Column(db.String(50))  # stock_in, stock_out, adjustment
    quantity_change = db.Column(db.Integer)
    remarks = db.Column(db.String(200))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='inventory_logs')
