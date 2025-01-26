from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService


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



@views.route('/place-order')
@login_required
def place_order():
    try:
        # Debug log untuk memastikan fungsi dipanggil
        print(f'User {current_user.id} is attempting to place an order...')
        
        customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
        if not customer_cart:
            flash('Your cart is empty')
            return redirect('/')
        
        # Debug log untuk jumlah item di keranjang
        print(f'Cart items: {len(customer_cart)}')
        
        total = 0
        for item in customer_cart:
            total += item.product.current_price * item.quantity

        # Debug total amount
        print(f'Total amount: {total}')
        
        service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
        create_order_response = service.collect.mpesa_stk_push(
            phone_number='081317694338',
            email=current_user.email,
            amount=total + 14000,
            narrative='Purchase'
        )
        
        # Debug response dari APIService
        print(f'Payment response: {create_order_response}')
        
        for item in customer_cart:
            new_order = Order(
                category=item.category,
                gender=item.gender,
                size=item.size,
                color=item.color,
                quantity=item.quantity,
                price=item.product.current_price,
                status=create_order_response['invoice']['state'].capitalize(),
                payment_id=create_order_response['id'],
                product_link=item.product_link,
                customer_link=item.customer_link
            )
            db.session.add(new_order)

            # Update stok produk
            product = Product.query.get(item.product_link)
            if product:
                product.in_stock -= item.quantity

            # Hapus item dari keranjang
            db.session.delete(item)

        db.session.commit()
        flash('Order Placed Successfully')
        return redirect('/orders')
    except Exception as e:
        db.session.rollback()
        print(f'Error placing order: {e}')
        flash('Order not placed. Please try again.')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')














