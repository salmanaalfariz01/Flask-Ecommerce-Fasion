from flask import Blueprint,render_template, flash, send_from_directory, redirect, url_for,request
from flask_login import login_required, current_user
from .forms import ShopItemsForm, UpdateItemsForm
from werkzeug.utils import secure_filename
from .models import Product, Customer
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

            # Check if the product already exists
            existing_product = Product.query.filter_by(
                product_name=product_name, size=size, color=color
            ).first()

            if existing_product:
                flash(f'Product: {product_name}, Size: {size}, Color: {color} already exists!', 'warning')
                return redirect(url_for('admin.add_shop_items'))

            # Save product image
            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            # Create new product entry
            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                size=size,
                category=category,
                gender=gender,
                color=color,
                in_stock=in_stock,
                flash_sale=flash_sale,
                product_picture=file_path,
            )

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'Product: {product_name}, Size: {size}, Color: {color} added successfully!', 'success')
                print('Product Added')
                return redirect(url_for('admin.add_shop_items'))
            except Exception as e:
                print(e)
                flash('Failed to add product!', 'danger')

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')



@admin.route('/product', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('product.html', items=items)
    return render_template('404.html')


@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = UpdateItemsForm()
        item_to_update = Product.query.get_or_404(item_id)

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

        if form.validate_on_submit():
            try:
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
                flash(f'Stock :{form.in_stock.data}, Size:{form.size.data}, Color:{form.size.data} updated successfully!', 'success')
                return redirect('/product')  # Pindah ke halaman /product
            except Exception as e:
                db.session.rollback()
                flash('Failed to update product.', 'danger')

        return render_template('update_item.html', form=form, item=item_to_update)

    return render_template('404.html')



@admin.route('/delete-item/<int:item_id>', methods=['POST', 'GET'])
@login_required
def delete_product(item_id):
    if current_user.id == 1:
        item = Product.query.get_or_404(item_id)

        try:
            db.session.delete(item)
            db.session.commit()
            flash("Product deleted successfully!", "success")
        except Exception as e:
            flash("Error deleting product!", "danger")
            print(e)

        return redirect(url_for("admin.shop_items"))

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









