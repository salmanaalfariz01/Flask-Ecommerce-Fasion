from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pytz import timezone


def get_jakarta_time():
    jakarta_timezone = timezone('Asia/Jakarta')
    return datetime.now(jakarta_timezone)


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20), unique=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    date_joined = db.Column(db.DateTime(timezone=True), default=get_jakarta_time)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))


    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return '<Customer %r>' % Customer.id


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Integer, nullable=False)
    previous_price = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Enum('men', 'women', 'child', name='gender_enum'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime(timezone=True), default=get_jakarta_time)

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return f'<Product {self.product_name}>'
    


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Enum('men', 'women', 'child', name='gender_enum'), nullable=False)
    size = db.Column(db.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # customer product

    def __str__(self):
        return '<Cart %r>' % self.id


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Enum('men', 'women', 'child', name='gender_enum'), nullable=False)
    size = db.Column(db.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('Pending', 'Paid', 'Shipped', 'Delivered', 'Cancelled', name='status_enum'), nullable=False)
    order_date = db.Column(db.DateTime(timezone=True), default=get_jakarta_time)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


    def __str__(self):
        return f'<Order {self.id}>'













