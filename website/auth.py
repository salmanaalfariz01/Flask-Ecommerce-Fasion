from flask import Blueprint, render_template, flash, redirect
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash




auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        address = form.address.data

        if password1 == password2:
            new_customer = Customer()
            new_customer.email = email
            new_customer.phone = phone
            new_customer.username = username
            new_customer.password_hash = generate_password_hash(password2)  # Hash password
            new_customer.address = address

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account created successfully! You can now log in.', 'success')  # Success message
                return redirect('/login')
            except Exception as e:
                print(e)
                flash('Account creation failed! The email might already exist.', 'error')  # Error message
        else:
            flash('Passwords do not match. Please try again.', 'error')

    return render_template('signup.html', form=form)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.email.data  # Menggunakan input login (email, phone, username)
        password = form.password.data

        # Mencari customer berdasarkan email, phone, atau username
        customer = Customer.query.filter(
            (Customer.email == login_input) | 
            (Customer.phone == login_input) | 
            (Customer.username == login_input)
        ).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect Email/Phone/Username or Password', 'error')
        else:
            flash('Account does not exist, please Sign Up', 'error')

    return render_template('login.html', form=form)



@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')


@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)


@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password Updated Successfully')
                return redirect(f'/profile/{customer.id}')
            else:
                flash('New Passwords do not match!!')

        else:
            flash('Current Password is Incorrect')

    return render_template('change_password.html', form=form)







