from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, IntegerField, PasswordField, EmailField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length



class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), Length(min=6)])
    address = TextAreaField('Address', validators=[DataRequired(), length(min=4)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')
    
class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), ])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Update Profile')


class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = IntegerField('Current Price', validators=[DataRequired()])
    previous_price = IntegerField('Previous Price', validators=[DataRequired()])
    size = SelectField(
        "Size",
        choices=[("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL")],
        default="S",
        validators=[DataRequired()],
    )
    category = SelectField(
        "Category",
        choices=[("Shirt", "Shirt")],
        default="Shirt",
        validators=[DataRequired()],
    )
    gender = SelectField(
        "Gender",
        choices=[("Men", "Men"), ("Women", "Women"), ("Child", "Child")],
        default="Men",
        validators=[DataRequired()],
    )
    color = StringField('Color', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')

    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')
    
class UpdateItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = IntegerField('Current Price', validators=[DataRequired()])
    previous_price = IntegerField('Previous Price', validators=[DataRequired()])
    size = StringField('Size', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    flash_sale = BooleanField('Flash Sale')

    update_product = SubmitField('Update')


class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])

    update = SubmitField('Update Status')





