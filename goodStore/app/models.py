# Import datetime for timestamping records
from datetime import datetime
# Import db and login_manager instances from the app initialization
from app import db, login_manager
# Import UserMixin which provides default implementations for Flask-Login required properties
from flask_login import UserMixin

# User loader callback for Flask-Login, helps retrieve a user by their ID from the session cache
@login_manager.user_loader
def load_user(user_id):
    """Retrieves the User object using their unique user_id"""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    User account model holding authentication and profile details.
    Inherits from db.Model (for database actions) and UserMixin (for login handling).
    """
    # Unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)
    # Username must be max 20 characters, unique across all users, and cannot be empty
    username = db.Column(db.String(20), unique=True, nullable=False)
    # Email must be valid, unique, and cannot be empty
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Profile picture filename, defaults to a standard image if unset
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    # Hashed password string, max length 60 characters
    password = db.Column(db.String(60), nullable=False)
    
    # Relationships linking the user to their historical orders and current cart items
    # 'backref' adds a virtual column indicating the owner, and 'lazy=True' loads data as needed
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart_items = db.relationship('CartItem', backref='customer', lazy=True)

    def __repr__(self):
        """String representation of the User object for debugging"""
        return f"User('{self.username}', '{self.email}')"

class Category(db.Model):
    """Represents a product classification category (e.g., Electronics, Clothing)"""
    id = db.Column(db.Integer, primary_key=True)
    # Category name must be unique
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Optional longer description of the category
    description = db.Column(db.Text, nullable=True)
    
    # Relationship linking the category to its child products
    products = db.relationship('Product', backref='category_ref', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}')"

class Product(db.Model):
    """Represents an item available for purchase in the store"""
    id = db.Column(db.Integer, primary_key=True)
    # Title or name of the product
    title = db.Column(db.String(100), nullable=False)
    # Detailed text description of the product features
    description = db.Column(db.Text, nullable=False)
    # Product cost in float/decimal representation
    price = db.Column(db.Float, nullable=False)
    # Pointer to the product image asset
    image_file = db.Column(db.String(20), nullable=False, default='placeholder.png')
    
    # Foreign Key linking this product back to its parent category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f"Product('{self.title}', '{self.price}')"

class CartItem(db.Model):
    """Represents a prospective purchase inside a user's shopping cart"""
    id = db.Column(db.Integer, primary_key=True)
    # How many of this specific item the user wants
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Foreign Keys identifying which product is being bought, and by whom
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to cleanly access product properties from the cart item
    product = db.relationship('Product')

class Order(db.Model):
    """Represents a completed checkout summarizing a purchase transaction"""
    id = db.Column(db.Integer, primary_key=True)
    # Timestamp marking exactly when the checkout occurred
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # The final combined cost of all products within the order
    total_price = db.Column(db.Float, nullable=False)
    # Delivery or processing status string
    status = db.Column(db.String(20), nullable=False, default='Completed')
    
    # Foreign Key denoting the buyer user account
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship linking this single order to its multiple individual purchased line-items
    order_items = db.relationship('OrderItem', backref='order_ref', lazy=True)

class OrderItem(db.Model):
    """Represents a single purchased line-item snapshot tied to an Order"""
    id = db.Column(db.Integer, primary_key=True)
    # The quantity purchased at the time of checkout
    quantity = db.Column(db.Integer, nullable=False)
    # Snapshot of the product price at the time of order (ignores future price changes)
    price = db.Column(db.Float, nullable=False)
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Relationship to extract underlying product name/details if needed
    product = db.relationship('Product')

