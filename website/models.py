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
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Enum('men', 'women', 'child', name='gender_enum'), nullable=False)
    size = db.Column(db.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # customer product

    def __str__(self):
        return '<Cart %r>' % self.id


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Enum('men', 'women', 'child', name='gender_enum'), nullable=False)
    size = db.Column(db.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('Pending', 'Paid', 'On Delivery', 'The order has arrived', name='status_enum'), nullable=False)
    shipping_cost = db.Column(db.Integer, nullable=False)
    grand_total = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime(timezone=True), default=get_jakarta_time)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    


    def __str__(self):
        return f'<Order {self.id}>'


class OrderUser(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Enum('men', 'women', 'child', name='gender_enum'), nullable=False)
    size = db.Column(db.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('Pending', 'Paid', 'On Delivery', 'The order has arrived', name='status_enum'), nullable=False)
    shipping_cost = db.Column(db.Integer, nullable=False)
    grand_total = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime(timezone=True), default=get_jakarta_time)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)



    def __str__(self):
        return f'<Order {self.id}>'


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)
    payment_number = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String(100), nullable=False)
    date_joined = db.Column(db.DateTime(timezone=True), default=get_jakarta_time)

    def __str__(self):
        return f'<Order {self.id}>'
    

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_user_id = db.Column(db.Integer, db.ForeignKey('order_user.id'), nullable=False)  # ID Order asli
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)  # Nama produk
    category = db.Column(db.String(50), nullable=False)  # Kategori produk
    gender = db.Column(db.String(10), nullable=True)  # Gender produk
    size = db.Column(db.String(10), nullable=True)  # Ukuran
    color = db.Column(db.String(20), nullable=True)  # Warna
    quantity = db.Column(db.Integer, nullable=False)  # Jumlah
    price = db.Column(db.Integer, nullable=False)  # Harga per produk
    shipping_cost = db.Column(db.Integer, nullable=False)  # Biaya pengiriman
    grand_total = db.Column(db.Integer, nullable=False)  # Total harga
    status = db.Column(db.String(50), nullable=False)  # Status pesanan
    date_completed = db.Column(db.DateTime(timezone=True), default=datetime.now)

    # Relasi
    customer = db.relationship('Customer', backref='histories')
    product = db.relationship('Product', backref='histories')















