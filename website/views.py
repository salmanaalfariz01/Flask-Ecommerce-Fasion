from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for, send_file
from flask_login import login_required, current_user
from .models import Product, Cart, Order, Payment, History, OrderUser
from . import db
from datetime import datetime
from pytz import timezone
from werkzeug.utils import secure_filename
import os
import io
import cv2
import random
import numpy as np
from sqlalchemy import text


# Menentukan folder untuk menyimpan foto pembayaran
UPLOAD_FOLDER = os.path.join('media', 'paid')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Memastikan folder ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_jakarta_time():
    jakarta_timezone = timezone('Asia/Jakarta')
    return datetime.now(jakarta_timezone)

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'


@views.route('/')
def home():
    # Query produk dengan flash_sale=True dan pastikan hasilnya selalu list
    items = Product.query.filter_by(flash_sale=True).all()  # Gunakan .all() untuk mendapatkan list

    # Pastikan items adalah list sebelum diacak
    if not isinstance(items, list):
        items = []

    # Acak produk hanya jika items berisi data
    shuffled_items = random.sample(items, len(items)) if items else []

    # Ambil data keranjang hanya jika user login
    cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []

    # Kirim data ke template
    return render_template('home.html', items=shuffled_items, cart=cart)



@views.route('/add-to-cart/<int:item_id>', methods=['GET'])
@login_required
def add_to_cart(item_id):
    # Ambil data dari query string
    product_name = request.args.get('product_name')
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
        product_id=item_id,
        customer_id=current_user.id,
        product_name=product_name,
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
            product_name=product_name,
            category=category,
            gender=gender,
            size=size,
            color=color,
            quantity=1,
            customer_id=current_user.id,
            product_id=item_id
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
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
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

        cart = Cart.query.filter_by(customer_id=current_user.id).all()

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
        cart = Cart.query.filter_by(customer_id=current_user.id).all()
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

        cart = Cart.query.filter_by(customer_id=current_user.id).all()

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
    customer_cart = Cart.query.filter_by(customer_id=current_user.id).all()  # Mengambil semua item cart untuk pengguna yang sedang login
    if customer_cart:
        try:
            total = 0  # Variabel untuk menghitung total harga pesanan
            amount = 0  # Variabel untuk menghitung jumlah produk
            shipping_cost = 14000  # Biaya pengiriman tetap, bisa diubah sesuai kebutuhan
            
            for item in customer_cart:
                # Menghitung harga per item (price x quantity)
                item_total = item.product.current_price * item.quantity
                total += item_total  # Total harga semua produk

                amount += item.quantity  # Menghitung total jumlah produk

            # Total harga + shipping
            grand_total = total + shipping_cost

            # Status pembayaran, misalnya 'pending', bisa diubah sesuai logika Anda
            payment_status = 'Pending'  # Status pesanan, bisa 'Pending', 'Paid', dsb.

            # Proses untuk menyimpan pesanan ke dalam tabel Order
            for item in customer_cart:
                new_order = Order()
                new_order.product_name = item.product.product_name
                new_order.category = item.product.category  # Kategori produk
                new_order.gender = item.product.gender      # Gender produk
                new_order.size = item.product.size          # Ukuran produk
                new_order.color = item.product.color        # Warna produk
                new_order.quantity = item.quantity          # Kuantitas produk yang dipesan
                new_order.price = item.product.current_price  # Harga produk
                new_order.status = payment_status           # Status pesanan
                new_order.shipping_cost = shipping_cost     # Biaya pengiriman
                new_order.grand_total = grand_total         # Total keseluruhan (harga + pengiriman)

                # Hubungkan pesanan dengan customer dan produk
                new_order.customer_id = item.customer_id
                new_order.product_id = item.product.id  # Link ke produk sesuai dengan id produk

                db.session.add(new_order)
                db.session.commit()  # Commit di sini untuk mendapatkan new_order.id yang baru saja dimasukkan

                # Simpan data pengguna ke tabel order_user, dengan data yang sama dari Order
                new_order_user = OrderUser(
                    id=new_order.id,  # Gunakan Order.id sebagai primary key untuk OrderUser
                    product_name = item.product.product_name,
                    category=item.product.category,
                    gender=item.product.gender,
                    size=item.product.size,
                    color=item.product.color,
                    quantity=item.quantity,
                    price=item.product.current_price,
                    status=payment_status,
                    shipping_cost=shipping_cost,
                    grand_total=grand_total,
                    customer_id=item.customer_id,
                    product_id=item.product.id
                )

                db.session.add(new_order_user)

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





@views.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    try:
        # Ambil pesanan berdasarkan ID dan pastikan pesanan milik pengguna yang sedang login
        order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first()

        if not order:
            flash('Order not found or you are not authorized to cancel this order.')
            return redirect('/orders')

        # Kembalikan kuantitas produk ke stok
        product = Product.query.get(order.product_id)
        if product:
            product.in_stock += order.quantity  # Tambahkan kembali jumlah produk yang dipesan ke stok

        # Hapus data terkait dari tabel order_user
        order_user = OrderUser.query.get(order.id)  # Menggunakan order.id karena sama dengan order_user.id
        if order_user:
            db.session.delete(order_user)

        # Hapus pesanan dari database
        db.session.delete(order)

        # Commit transaksi ke database
        db.session.commit()

        flash('Order has been canceled successfully.')
        return redirect('/orders')

    except Exception as e:
        db.session.rollback()  # Rollback jika ada kesalahan
        print(f"Error: {e}")
        flash('Failed to cancel the order.')
        return redirect('/orders')




@views.route('/orders')
@login_required
def order():
    # Cek apakah pengguna adalah admin
    is_admin = current_user.id == 1

    # Admin dapat melihat semua pesanan, pengguna biasa hanya melihat pesanan mereka sendiri
    if is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(customer_id=current_user.id).all()

    # Menggunakan query SQL mentah untuk mendapatkan semua metode pembayaran
    sql_payments = text("""
        SELECT name, payment_method, payment_number, picture
        FROM payment
    """)
    payments = db.session.execute(sql_payments).fetchall()

    # Hitung jumlah dan total untuk setiap order
    for item in orders:
        item.amount = item.quantity  # Jumlah produk yang dipesan
        item.total = item.price * item.quantity  # Total harga pesanan

    return render_template('orders.html', orders=orders, payments=payments, is_admin=is_admin)

@views.route('/upload-payment/<int:order_id>', methods=['POST'])
@login_required
def upload_payment(order_id):
    # Ambil data order berdasarkan order_id
    order = Order.query.get(order_id)
    
    # Pastikan order ada dan pemiliknya adalah customer yang sedang login
    if order and order.customer_id == current_user.id:
        # Periksa apakah ada file yang diunggah
        if 'payment_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['payment_file']
        
        # Pastikan file yang diunggah valid
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Update status pesanan menjadi "Paid" di tabel Order
            order.status = 'Paid'
            
            # Update status pesanan menjadi "Paid" di tabel OrderUser
            order_user = OrderUser.query.get(order.id)  # Mengambil OrderUser berdasarkan order.id
            if order_user:
                order_user.status = 'Paid'
                db.session.commit()

            flash('Payment uploaded successfully and order marked as Paid!')
            return redirect(url_for('views.order'))
        else:
            flash('Invalid file format! Only JPG, JPEG, and PNG are allowed.')
            return redirect(request.url)
    
    flash('Order not found or unauthorized access.')
    return redirect(url_for('views.order'))






def wrap_text(text, font, font_scale, max_width, thickness):
    """
    Fungsi untuk memecah teks menjadi beberapa baris agar muat dalam lebar gambar
    """
    words = text.split(' ')
    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = current_line + ' ' + word
        (w, h), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
        
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)  # Menambahkan baris terakhir
    return lines

def generate_invoice_png(order_id):
    # Ambil data pesanan berdasarkan order_id
    order = Order.query.get(order_id)
    if order:
        # Pastikan customer terkait ditemukan
        customer = order.customer
        if not customer:
            return None

        # Dimensi gambar (ukuran kertas diperbesar)
        width, height = 900, 900
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        # Font dan pengaturan teks (gunakan font tebal)
        font = cv2.FONT_HERSHEY_DUPLEX  # Font tebal untuk seluruh teks
        font_scale = 0.8
        bold_font_scale = 0.9
        color = (0, 0, 0)  # Warna hitam
        bold_thickness = 2  # Ketebalan font untuk teks bold
        line_height = 40
        margin_left = 50

        # Teks header
        y_offset = 50
        cv2.putText(img, f"Invoice for Order ID: {order.id}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        # Informasi pesanan
        y_offset += line_height
        cv2.putText(img, f"Name: {order.product_name}", (margin_left, y_offset), font, font_scale, color, bold_thickness)
        
        y_offset += line_height
        cv2.putText(img, f"Category: {order.category}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Gender: {order.gender}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Size: {order.size}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Color: {order.color}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Quantity: {order.quantity}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Price: Rp {order.price:,}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Shipping Cost: Rp {order.shipping_cost:,}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Total: Rp {order.grand_total:,}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Order Status: {order.status}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        # Informasi customer
        y_offset += 2 * line_height
        cv2.putText(img, "Customer Details:", (margin_left, y_offset), font, bold_font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Username: {customer.username}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Email: {customer.email}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        y_offset += line_height
        cv2.putText(img, f"Phone: {customer.phone}", (margin_left, y_offset), font, font_scale, color, bold_thickness)

        # Alamat dipecah menjadi beberapa baris dengan word wrapping
        y_offset += line_height
        cv2.putText(img, "Address:", (margin_left, y_offset), font, bold_font_scale, color, bold_thickness)

        address_lines = wrap_text(customer.address, font, font_scale, width - 2 * margin_left, bold_thickness)
        for line in address_lines:
            y_offset += line_height
            cv2.putText(img, line, (margin_left, y_offset), font, font_scale, color, bold_thickness)

        # Simpan gambar ke buffer
        buffer = io.BytesIO()
        _, img_encoded = cv2.imencode(".png", img)
        buffer.write(img_encoded)
        buffer.seek(0)
        return buffer
    return None




@views.route('/mark-as-paid/<int:order_id>', methods=['POST'])
@login_required
def mark_as_paid(order_id):
    order = Order.query.get(order_id)
    if order:
        order.status = 'Paid'
        db.session.commit()

        # Update status di order_user menjadi "Paid"
        order_user = OrderUser.query.filter_by(order_id=order.id, customer_id=current_user.id).first()
        if order_user:
            order_user.status = 'Paid'
            db.session.commit()

        flash("Order marked as paid and invoice is ready!")
        return redirect(f'/download-invoice/{order.id}')
    flash("Order not found!")
    return redirect('/orders')

@views.route('/mark-as-delivery/<int:order_id>', methods=['POST'])
@login_required
def mark_as_delivery(order_id):
    # Hanya admin yang dapat menandai pesanan sebagai "On Delivery"
    if current_user.id != 1:
        flash("You are not authorized to perform this action.")
        return redirect('/orders')

    # Ambil pesanan berdasarkan ID
    order = Order.query.get(order_id)
    if order:
        # Update status pesanan menjadi "On Delivery" di tabel Order
        order.status = "On Delivery"
        db.session.commit()

        # Update status pesanan menjadi "On Delivery" di tabel OrderUser
        order_user = OrderUser.query.get(order.id)  # Ambil data OrderUser berdasarkan order.id yang sama
        if order_user:
            order_user.status = 'On Delivery'
            db.session.commit()

        flash(f"Order {order.id} marked as On Delivery.")
    else:
        flash("Order not found.")

    return redirect('/orders')


# Route untuk mengunduh invoice
@views.route('/download-invoice/<int:order_id>', methods=['GET'])
@login_required
def download_invoice(order_id):
    # Generate invoice PNG
    invoice = generate_invoice_png(order_id)

    if invoice:
        # Mengunduh file PNG
        return send_file(invoice, as_attachment=True, download_name=f"invoice_{order_id}.png", mimetype="image/png")
    else:
        flash("Invoice not found!")
        return redirect('/orders')

@views.route('/order-arrived/<int:order_user_id>', methods=['POST'])
@login_required
def order_arrived(order_user_id):
    # Ambil data OrderUser berdasarkan order_user_id
    order_user = OrderUser.query.get(order_user_id)

    if not order_user:
        flash("Order not found.", "error")
        return redirect(url_for('views.order'))  # Gantilah ini jika perlu

    # Pastikan hanya user yang membuat pesanan ini yang dapat mengonfirmasi
    if order_user.customer_id != current_user.id:
        flash("You are not authorized to confirm this order.", "error")
        return redirect(url_for('views.order'))  # Gantilah ini jika perlu

    # Simpan data dari order_user ke history
    history = History(
        order_user_id=order_user.id,  # Gunakan order_user.id yang sesuai
        customer_id=order_user.customer_id,
        product_id=order_user.product_id,
        product_name=order_user.product_name,
        category=order_user.category,
        gender=order_user.gender,
        size=order_user.size,
        color=order_user.color,
        quantity=order_user.quantity,
        price=order_user.price,
        shipping_cost=order_user.shipping_cost,
        grand_total=order_user.grand_total,
        status="Completed"
    )
    db.session.add(history)

    # Hapus pesanan dari tabel Order
    order = Order.query.get(order_user.id)  # Ambil pesanan dari tabel Order menggunakan ID yang sama
    if order:
        db.session.delete(order)

    db.session.commit()

    flash("Order marked as completed and moved to history.", "success")
    return redirect(url_for('views.history'))  # Pastikan ke halaman yang benar






@views.route('/history')
@login_required
def history():
    # Admin melihat semua riwayat, user melihat riwayat mereka sendiri
    if current_user.id == 1:  # Admin
        histories = History.query.all()
    else:
        histories = History.query.filter_by(customer_id=current_user.id).all()

    return render_template('history.html', histories=histories)




@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')










