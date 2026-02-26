# Import core Flask components (Blueprint for modular routes, render_template for HTML, url_for for route generation, flash for alerts, redirect for navigation, request for HTTP data)
from flask import Blueprint, render_template, url_for, flash, redirect, request
# Import the initialized database and password hashing instances
from app import db, bcrypt
# Import all database models needed for the views
from app.models import User, Category, Product, CartItem, Order, OrderItem
# Import authentication management helpers from Flask-Login
from flask_login import login_user, current_user, logout_user, login_required

# Create a Blueprint object named 'main'
# Blueprints group related routes together, making the application modular
bp = Blueprint('main', __name__)

@bp.context_processor
def inject_cart_count():
    """
    Context processor that runs before rendering *any* template.
    It calculates the total number of items in the current user's cart
    and injects it into every HTML template as the variable 'cart_count'.
    This allows the navbar to always show the correct cart count.
    """
    # Only calculate if the user is authenticated via Flask-Login
    if current_user.is_authenticated:
        # Fetch all cart items for the currently logged-in user
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        # Sum the quantities of all individual item rows
        cart_count = sum(item.quantity for item in cart_items)
        # Return a dictionary containing the variable available to templates
        return dict(cart_count=cart_count)
    # If not logged in, return 0 for the cart count
    return dict(cart_count=0)

@bp.route('/')
def home():
    """
    Homepage Route.
    Fetches categories and a limited number of featured products to display.
    """
    # Retrieve all categories from the database
    categories = Category.query.all()
    # Featured products: retrieve the first 8 products for the homepage grid
    featured_products = Product.query.limit(8).all()
    # Render the index template and pass the queried data to it
    return render_template('index.html', categories=categories, featured_products=featured_products)

@bp.route('/category/<int:category_id>')
def category_view(category_id):
    """
    Dynamic route to view all products within a specific category.
    The <int:category_id> part of the URL gets passed to this function as an integer.
    """
    # Fetch the category or automatically return a 404 Not Found error if it doesn't exist
    category = Category.query.get_or_404(category_id)
    # The 'category' object contains its related products due to the db.relationship
    return render_template('category.html', category=category)

@bp.route('/product/<int:product_id>')
def product_view(product_id):
    """
    Dynamic route to view detailed information for a single product.
    """
    # Fetch the product by its ID or automatically 404
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration Route. Handles both displaying the form (GET)
    and processing the form submission (POST).
    """
    # If the user is already logged in, redirect them away from the registration page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # If the browser sent data via a POST request form submission
    if request.method == 'POST':
        # Extract the user inputs from the submitted form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if a user with that email or username already exists in the database
        user_exists = User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()
        if user_exists:
            # Send an error alert to the user's screen
            flash('Email or username already exists. Please login or use a different one.', 'danger')
            # Reload the registration page
            return redirect(url_for('main.register'))

        # Securely hash the user's password before storing it (never store plain text)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # Create a new User object instance
        user = User(username=username, email=email, password=hashed_password)
        
        # Stage the new user object for database insertion
        db.session.add(user)
        # Commit the transaction to officially write it to the db
        db.session.commit()
        
        # Send a success message and redirect them to the login page
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    
    # For GET requests, simply render the blank registration HTML form
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login Route. Authenticates users.
    """
    # Prevent logged-in users from accessing the login page again
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Get the login credentials from the form submitted
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Attempt to fetch the user record attached to the provided email
        user = User.query.filter_by(email=email).first()
        
        # Verify the user exists AND the provided password matches the hashed password
        if user and bcrypt.check_password_hash(user.password, password):
            # Tell Flask-Login to officially log the user in, setting up session cookies
            login_user(user)
            
            # If the user was redirected here from a protected page, next_page contains that original destination
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            
            # Send them to the original destination, or the homepage if none
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            # Provide vague feedback for security if login fails
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """
    Logout Route. Clears the user's session.
    """
    # Tell Flask-Login to wipe the session cookie
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@bp.route('/cart')
@login_required # This decorator forces users to be logged in to view this page
def cart():
    """
    Shopping Cart View Route.
    """
    # Fetch all items sitting in the current user's active cart
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    # Calculate the grand total financial cost of the cart items
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Render the cart page with the items and calculated total
    return render_template('cart.html', cart_items=cart_items, total=total)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """
    Endpoint to add a chosen product to the user's shopping cart.
    Accepts POST requests normally triggered by a "Add to Cart" button.
    """
    # Verify the product exists
    product = Product.query.get_or_404(product_id)
    # Extract quantity from the form, defaulting to 1
    quantity = int(request.form.get('quantity', 1))
    
    # Check if this exact item is already in the user's cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    
    if cart_item:
        # If it exists, simply increase the quantity count
        cart_item.quantity += quantity
    else:
        # If it's a new item, create a new CartItem record
        cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)
        
    # Commit changes to the database
    db.session.commit()
    flash(f'{product.title} has been added to your cart.', 'success')
    
    # Redirect the user back to whatever page they were just on, or home as a fallback
    return redirect(request.referrer or url_for('main.home'))

@bp.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """
    Endpoint to delete a specific item row from the user's cart.
    """
    # Fetch the exact cart item record
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Security check: Ensure the user actually owns the cart item they are trying to delete
    if cart_item.user_id == current_user.id:
        # Delete the item from the database
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'info')
        
    # Redirect back to the cart page
    return redirect(url_for('main.cart'))

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """
    Checkout Processing Endpoint.
    Converts CartItems into a finalized Order and OrderItems.
    """
    # Fetch everything in the user's current cart
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Safegaurd preventing empty checkouts
    if not cart_items:
        flash('Your cart is empty. Please add items to checkout.', 'warning')
        return redirect(url_for('main.cart'))

    # Calculate final grand total based on the current product prices
    total = sum(item.product.price * item.quantity for item in cart_items)
    # Create the top-level Order record
    order = Order(user_id=current_user.id, total_price=total)
    db.session.add(order)
    # Commit immediately to generate an Order ID
    db.session.commit()

    # Loop through each item in the cart to link it to the newly created order
    for item in cart_items:
        # Create an OrderItem snapshot (locking in the quantity and current price)
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(order_item)
        
        # Remove the item from the active cart since it has now been purchased
        db.session.delete(item)
    
    # Commit all individual order items and cart item deletions to the db
    db.session.commit()
    
    flash('Your order has been placed successfully! Thank you for shopping with goodStore.', 'success')
    # Return the user to the homepage after a successful purchase
    return redirect(url_for('main.home'))

