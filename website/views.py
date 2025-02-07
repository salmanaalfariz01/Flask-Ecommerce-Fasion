from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for, send_file
from flask_login import login_required, current_user
from .models import Product, Cart, Order, PaymentStatus, History, OrderUser, get_jakarta_time
from . import db
from datetime import datetime, timedelta
from pytz import timezone
from werkzeug.utils import secure_filename
import os
import io
import cv2
import random
import string
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


views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'


@views.route('/', methods=['GET', 'POST'])
def home():
    # Ambil parameter pencarian dan filter dari URL query
    search_query = request.args.get('search', '')
    gender_filter = request.args.get('gender', '')
    size_filter = request.args.get('size', '')

    # Mulai query untuk produk dengan filter flash_sale
    query = Product.query.filter_by(flash_sale=True)

    # Terapkan filter pencarian berdasarkan nama produk
    if search_query:
        query = query.filter(Product.product_name.ilike(f'%{search_query}%'))

    # Terapkan filter berdasarkan gender
    if gender_filter:
        query = query.filter_by(gender=gender_filter)

    # Terapkan filter berdasarkan ukuran (size)
    if size_filter:
        query = query.filter_by(size=size_filter)

    # Ambil data produk yang sudah difilter
    items = query.all()

    # Acak urutan produk menggunakan random.shuffle
    random.shuffle(items)

    # Ambil data keranjang (jika user login)
    cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []

    # Kirim data ke template dengan filter yang diterapkan
    return render_template(
        'home.html',
        items=items,
        cart=cart,
        search=search_query,
        gender=gender_filter,
        size=size_filter
    )



# Halaman About
@views.route('/about')
@login_required
def about():
    cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []
    return render_template('about.html', cart=cart)

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

    # Redirect kembali ke halaman utama
    return redirect(url_for('views.home'))


@views.route('/cart')
@login_required
def show_cart():
    # Ambil semua item dari keranjang berdasarkan customer_id
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+14000)


@views.route('/removecart/<int:cart_id>', methods=['GET'])
@login_required
def remove_cart(cart_id):
    # Mencari item di keranjang berdasarkan cart_id dan customer_id
    cart_item = Cart.query.filter_by(id=cart_id, customer_id=current_user.id).first()

    if not cart_item:
        flash("Item not found!", "error")  # Kategori "error" untuk item yang tidak ditemukan
        return redirect(url_for('views.show_cart'))

    # Hapus item dari keranjang
    db.session.delete(cart_item)
    try:
        db.session.commit()
        flash("Item removed from cart!", "remove")  # Kategori "remove" untuk penghapusan item
    except Exception as e:
        db.session.rollback()
        flash("Failed to remove item. Please try again.", "error")

    # Redirect ke halaman keranjang
    return redirect(url_for('views.show_cart'))

@views.route('/pluscart')
@login_required
def plus_cart():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.filter_by(id=cart_id, customer_id=current_user.id).first()

    if not cart_item:
        return jsonify({'error': 'Invalid cart item'}), 400

    # Tambah kuantitas
    cart_item.quantity += 1
    db.session.commit()

    # Menghitung total baru
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = sum(item.product.current_price * item.quantity for item in cart)

    return jsonify({
        'quantity': cart_item.quantity,  # Mengirim kuantitas terbaru
        'total': amount + 14000  # Total dengan biaya pengiriman
    })

@views.route('/minuscart')
@login_required
def minus_cart():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.filter_by(id=cart_id, customer_id=current_user.id).first()

    if not cart_item:
        return jsonify({'error': 'Invalid cart item'}), 400

    # Kurangi kuantitas jika lebih dari 1
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.session.commit()

    # Menghitung total baru
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = sum(item.product.current_price * item.quantity for item in cart)

    return jsonify({
        'quantity': cart_item.quantity,  # Mengirim kuantitas terbaru
        'total': amount + 14000  # Total dengan biaya pengiriman
    })


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
                new_order.product_picture = item.product.product_picture
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
                    product_picture = item.product.product_picture,
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
        # Cek apakah pengguna adalah admin
        is_admin = current_user.id == 1

        # Jika admin, ambil pesanan berdasarkan order_id tanpa memeriksa customer_id
        if is_admin:
            order = Order.query.get(order_id)
        else:
            # Jika bukan admin, hanya ambil pesanan yang milik pengguna yang sedang login
            order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first()

        if not order:
            flash('Order not found or you are not authorized to cancel this order.', 'error')
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

        flash('Order has been canceled successfully.', 'remove')
        return redirect('/orders')

    except Exception as e:
        db.session.rollback()  # Rollback jika ada kesalahan
        print(f"Error: {e}")
        flash('Failed to cancel the order. Please try again later.', 'error')
        return redirect('/orders')

    



@views.route('/orders')
@login_required
def order():
    # Cek apakah pengguna adalah admin
    is_admin = current_user.id == 1

    # Jika admin, tampilkan semua pesanan
    if is_admin:
        orders = Order.query.all()
    else:
        # Jika pengguna biasa, hanya tampilkan pesanan mereka sendiri
        orders = Order.query.filter_by(customer_id=current_user.id).all()
        

    # Menggunakan query SQL mentah untuk mendapatkan semua metode pembayaran
    sql_payments = text(""" 
        SELECT name, payment_method, payment_number, picture 
        FROM payment 
    """)
    payments = db.session.execute(sql_payments).fetchall()

    # Ambil data keranjang (jika user login)
    cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []

    # Hitung jumlah dan total untuk setiap order
    for item in orders:
        item.amount = item.quantity  # Jumlah produk yang dipesan
        item.total = item.price * item.quantity  # Total harga pesanan

    return render_template('orders.html', orders=orders, payments=payments, is_admin=is_admin, cart=cart)



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
            
            # Menambahkan 10 angka acak ke nama file
            random_suffix = ''.join(random.choices(string.digits, k=10))
            filename_with_suffix = f"{filename.split('.')[0]}_{random_suffix}.{filename.split('.')[-1]}"
            
            file_path = os.path.join(UPLOAD_FOLDER, filename_with_suffix)
            file.save(file_path)
            
            # Update status pesanan menjadi "Paid" di tabel Order
            order.status = 'Paid'
            
            # Update status pesanan menjadi "Paid" di tabel OrderUser
            order_user = OrderUser.query.get(order.id)  # Mengambil OrderUser berdasarkan order.id
            if order_user:
                order_user.status = 'Paid'
                db.session.commit()

            # Extracting the product details from the order object
            product_name = order.product_name
            product_picture = order.product_picture
            product_category = order.category
            gender = order.gender
            size = order.size
            color = order.color
            quantity = order.quantity
            price = order.price
            shipping_cost = order.shipping_cost
            total = order.grand_total

            # Insert into payment_status table
            payment_status = PaymentStatus(
                order_id=order.id,
                status='Paid',  # Status of the payment
                payment_file_path=file_path,  # Store the file path or any other info you need
                product_name=product_name,  # Product name from the order
                product_picture=product_picture,  # Product picture from the order
                product_category=product_category,
                gender=gender,
                size=size,
                color=color,
                quantity=quantity,
                price=price,
                shipping_cost=shipping_cost,
                total=total
            )
            db.session.add(payment_status)  # Add the new payment status to the session
            db.session.commit()  # Commit the transaction to the database

            flash('Payment uploaded successfully and order marked as Paid!')
            return redirect(url_for('views.order'))
        else:
            flash('Invalid file format! Only JPG, JPEG, and PNG are allowed.')
            return redirect(request.url)
    
    flash('Order not found or unauthorized access.')
    return redirect(url_for('views.order'))



@views.route('/payment-status')
@login_required
def payment_status():
    # Retrieve all payment status records
    payments = PaymentStatus.query.all()
    
    # Ambil data keranjang (jika user login)
    cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []

    # Render the payment status page, passing the payment records
    return render_template('payment_status.html', payments=payments, cart=cart)





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
        flash("You are not authorized to perform this action.", "error")
        return redirect('/orders')

    try:
        # Ambil pesanan berdasarkan ID
        order = Order.query.get(order_id)
        if not order:
            flash("Order not found.", "error")
            return redirect('/orders')

        # Update status pesanan menjadi "On Delivery" di tabel Order
        order.status = "On Delivery"

        # Update status pesanan menjadi "On Delivery" di tabel OrderUser
        order_user = OrderUser.query.get(order.id)
        if order_user:
            order_user.status = 'On Delivery'

        # Update status pesanan menjadi "On Delivery" di tabel PaymentStatus
        payment_status = PaymentStatus.query.filter_by(order_id=order.id).first()
        if payment_status:
            payment_status.status = 'On Delivery'

        # Simpan semua perubahan dalam satu transaksi
        db.session.commit()
        
        flash(f"Order {order.id} marked as On Delivery.", "success")

    except Exception as e:
        db.session.rollback()  # Rollback jika terjadi kesalahan
        print(f"Error: {e}")
        flash("Failed to update order status.", "error")

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


@views.route('/order-arrived/<int:id>', methods=['POST'])
@login_required
def order_arrived(id):
    # Ambil data OrderUser berdasarkan order_user_id
    order_user = OrderUser.query.get(id)

    if not order_user:
        flash("Order not found.", "error")
        return redirect(url_for('views.order'))  # Gantilah ini jika perlu

    # Pastikan hanya user yang membuat pesanan ini yang dapat mengonfirmasi
    if order_user.customer_id != current_user.id:
        flash("You are not authorized to confirm this order.", "error")
        return redirect(url_for('views.order'))  # Gantilah ini jika perlu

    try:
        # Debugging: Periksa apakah order_user.id ada
        print(f"order_user_id: {order_user.id}")  # Log ID order_user untuk memastikan nilai
        
        # Simpan data dari order_user ke history
        history = History(
            customer_id=order_user.customer_id,
            product_id=order_user.product_id,
            product_name=order_user.product_name,
            product_picture=order_user.product_picture,
            category=order_user.category,
            gender=order_user.gender,
            size=order_user.size,
            color=order_user.color,
            quantity=order_user.quantity,
            price=order_user.price,
            shipping_cost=order_user.shipping_cost,
            grand_total=order_user.grand_total,
            status="The Order Has Arrived"
        )
        
        db.session.add(history)

        # Debugging log untuk memeriksa status session
        print(f"Session new: {db.session.new}")  # Cek objek baru yang ditambahkan
        print(f"Session dirty: {db.session.dirty}")  # Cek objek yang telah dimodifikasi
        
        # Simpan perubahan ke database
        db.session.commit()

        # Debugging log
        print(f"✅ Data order {order_user.id} masuk ke history!")

        # Hapus pesanan dari tabel Order
        order = Order.query.get(order_user.id)
        if order:
            db.session.delete(order)

        # Hapus data payment_status terkait order_user_id
        payment_status = PaymentStatus.query.filter_by(order_id=order_user.id).first()
        if payment_status:
            db.session.delete(payment_status)

        # Hapus order_user setelah semua data telah disimpan ke history
        db.session.delete(order_user)

        db.session.commit()  # Commit semua perubahan

        flash("Order marked as completed and moved to history.", "success")
        return redirect(url_for('views.history'))  # Redirect ke halaman history

    except Exception as e:
        db.session.rollback()  # Rollback jika ada error
        print(f"❌ ERROR: {e}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for('views.order'))







@views.route('/history')
@login_required
def history():
    # Admin melihat semua riwayat, user melihat riwayat mereka sendiri
    if current_user.id == 1:  # Admin
        histories = History.query.all()
    else:
        histories = History.query.filter_by(customer_id=current_user.id).all()
    
    
    # Ambil data keranjang (jika user login)
    cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []

    return render_template('history.html', histories=histories, cart=cart)





