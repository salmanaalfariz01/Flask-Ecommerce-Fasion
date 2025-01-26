from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order, Payment
from flask_login import login_required, current_user
from . import db
from datetime import datetime
from pytz import timezone


def get_jakarta_time():
    jakarta_timezone = timezone('Asia/Jakarta')
    return datetime.now(jakarta_timezone)

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'




@views.route('/')
def home():

    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/add-to-cart/<int:item_id>', methods=['GET'])
@login_required
def add_to_cart(item_id):
    # Ambil data dari query string
    category = request.args.get('category')
    gender = request.args.get('gender')
    size = request.args.get('size')
    color = request.args.get('color')

    # Ambil produk berdasarkan ID
    item_to_add = Product.query.get(item_id)
    if not item_to_add:
        flash('Product not found')
        return redirect(request.referrer)

    # Periksa apakah item sudah ada di keranjang dengan parameter tambahan
    item_exists = Cart.query.filter_by(
        product_link=item_id,
        customer_link=current_user.id,
        category=category,
        gender=gender,
        size=size,
        color=color
    ).first()

    if item_exists:
        try:
            # Jika sudah ada, tambahkan quantity
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantity of {item_exists.product.product_name} has been updated')
        except Exception as e:
            db.session.rollback()
            print('Error updating quantity:', e)
            flash(f'Failed to update quantity for {item_exists.product.product_name}')
    else:
        # Jika belum ada, tambahkan item baru ke keranjang
        new_cart_item = Cart(
            category=category,
            gender=gender,
            size=size,
            color=color,
            quantity=1,
            customer_link=current_user.id,
            product_link=item_id
        )
        try:
            db.session.add(new_cart_item)
            db.session.commit()
            flash(f'{new_cart_item.product.product_name} added to cart')
        except Exception as e:
            db.session.rollback()
            print('Error adding item to cart:', e)
            flash(f'Failed to add {item_to_add.product_name} to cart')

    return redirect(request.referrer)





@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+14000)


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 14000
        }

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)

        # Ensure quantity does not go below 0
        if cart_item.quantity > 0:
            cart_item.quantity = cart_item.quantity - 1
            db.session.commit()

        # Get the updated cart and calculate the total amount
        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        # Add shipping cost to the total
        data = {
            'quantity': cart_item.quantity,  # This will be 0 if quantity was 0 before update
            'amount': amount,
            'total': amount + 14000  # Assuming shipping cost is 14000
        }

        return jsonify(data)



@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 14000
        }

        return jsonify(data)



@views.route('/place-order', methods=['POST'])
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()  # Mengambil semua item cart untuk pengguna yang sedang login
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            # Status pembayaran, misalnya 'pending', bisa diubah sesuai logika Anda
            payment_status = 'Pending'  # Status pesanan, bisa 'Pending', 'Paid', dsb.

            # Proses untuk menyimpan pesanan ke dalam tabel Order
            for item in customer_cart:
                new_order = Order()
                new_order.category = item.product.category  # Kategori produk
                new_order.gender = item.product.gender      # Gender produk
                new_order.size = item.product.size          # Ukuran produk
                new_order.color = item.product.color        # Warna produk
                new_order.quantity = item.quantity          # Kuantitas produk yang dipesan
                new_order.price = item.product.current_price  # Harga produk
                new_order.status = payment_status           # Status pesanan

                # Hubungkan pesanan dengan customer dan produk
                new_order.customer_link = item.customer_link
                new_order.product_link = item.product.id  # Link ke produk sesuai dengan id produk

                db.session.add(new_order)

                # Mengurangi stok produk
                product = Product.query.get(item.product.id)  # Ambil produk berdasarkan ID
                if product:
                    product.in_stock -= item.quantity  # Kurangi stok produk sesuai dengan kuantitas yang dipesan
                    db.session.commit()

                # Menghapus item dari keranjang setelah pemesanan berhasil
                db.session.delete(item)

            db.session.commit()  # Commit transaksi database

            flash('Order Placed Successfully')
            return redirect('/orders')  # Arahkan pengguna ke halaman daftar pesanan setelah berhasil
        except Exception as e:
            db.session.rollback()  # Jika terjadi kesalahan, rollback transaksi
            print(e)
            flash('Order not placed')
            return redirect('/')
    else:
        flash('Your cart is Empty')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    # Ambil semua pesanan berdasarkan pengguna yang sedang login
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    
    # Ambil semua metode pembayaran
    payments = Payment.query.all()  # Ambil data payment dari tabel Payment
    
    return render_template('orders.html', orders=orders, payments=payments)





@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')














