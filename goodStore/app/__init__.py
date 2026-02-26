# Import the core Flask class used to create the application instance
from flask import Flask
# Import SQLAlchemy for Object Relational Mapping (database interactions)
from flask_sqlalchemy import SQLAlchemy
# Import Bcrypt for securely hashing and verifying passwords
from flask_bcrypt import Bcrypt
# Import LoginManager for handling user authentication state and sessions
from flask_login import LoginManager
# Import the OS module for path manipulation
import os

# Initialize database extension - using uninitialized instance here allows for the app factory pattern
db = SQLAlchemy()
# Initialize password hashing extension
bcrypt = Bcrypt()
# Initialize login management extension
login_manager = LoginManager()

# Set the route/endpoint name that the login manager should redirect to if a user needs to log in
login_manager.login_view = 'main.login'
# Set the Bootstrap alert CSS category for login messages (e.g., 'info', 'success', 'danger')
login_manager.login_message_category = 'info'

def create_app():
    """
    Application Factory Function.
    Creates, configures, and initializes the Flask application instance.
    This pattern improves modularity and makes testing easier.
    """
    # Create the Flask application object
    app = Flask(__name__)
    
    # Configure the secret key used for session security and CSRF protection
    app.config['SECRET_KEY'] = 'dev-secret-key-12345' # Important: change this in production!
    
    # Determine the absolute path to the directory containing this config file
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Set the SQLite database location, placing it alongside this file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
    # Disable modification tracking feature to save memory/resources
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize all previously defined extensions with the newly created app instance
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import the main blueprint which contains all application routes
    # Imported inside the function to avoid circular imports
    from app.routes import bp
    # Register the blueprint with the application to activate the defined routes
    app.register_blueprint(bp)

    # Return the fully configured application instance
    return app

