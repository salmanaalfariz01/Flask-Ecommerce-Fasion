from flask import Blueprint, render_template, flash, send_from_directory, redirect, request
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrderForm, UpdateItemsForm
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer
from . import db


admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)


@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            size = form.size.data
            category = form.category.data
            gender = form.gender.data
            color = form.color.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data

            file_name = secure_filename(file.filename)

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.size = size
            new_shop_item.category = category
            new_shop_item.gender = gender
            new_shop_item.color = color
            new_shop_item.in_stock = in_stock
            new_shop_item.flash_sale = flash_sale

            new_shop_item.product_picture = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} Size: {size} Color: {color} added Successfully')
                print('Product Added')
                return render_template('add_shop_items.html', form=form)
            except Exception as e:
                print(e)
                flash('Product Not Added!!')

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')


@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')



@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = UpdateItemsForm()

        # Query produk berdasarkan ID
        item_to_update = Product.query.get_or_404(item_id)

        # Log untuk debugging
        print("Request Method:", request.method)
        print("Form Data:", request.form)

        # Saat request GET, isi nilai form dengan data dari database
        if request.method == 'GET':
            form.product_name.data = item_to_update.product_name
            form.previous_price.data = item_to_update.previous_price
            form.current_price.data = item_to_update.current_price
            form.size.data = item_to_update.size
            form.category.data = item_to_update.category
            form.gender.data = item_to_update.gender
            form.color.data = item_to_update.color
            form.in_stock.data = item_to_update.in_stock
            form.flash_sale.data = item_to_update.flash_sale

        # Jika form divalidasi (saat POST)
        if form.validate_on_submit():
            print("Form Validated")
            try:
                # Update data produk di database
                item_to_update.product_name = form.product_name.data
                item_to_update.previous_price = form.previous_price.data
                item_to_update.current_price = form.current_price.data
                item_to_update.size = form.size.data
                item_to_update.category = form.category.data
                item_to_update.gender = form.gender.data
                item_to_update.color = form.color.data
                item_to_update.in_stock = form.in_stock.data
                item_to_update.flash_sale = form.flash_sale.data

                db.session.commit()
                flash(f'Product "{form.product_name.data}" updated successfully!', 'success')
                return redirect('/shop-items')
            except Exception as e:
                db.session.rollback()
                print("Error Updating Product:", e)
                flash('Failed to update product.', 'danger')

        # Jika form tidak valid (saat POST)
        if request.method == 'POST' and not form.validate_on_submit():
            print("Form Validation Failed")

        # Render template dengan form dan data produk
        return render_template('update_item.html', form=form, item=item_to_update)

    # Jika bukan admin, kembalikan 404
    return render_template('404.html')



@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
        return redirect('/shop-items')

    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} Updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')









