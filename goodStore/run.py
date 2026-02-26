# Import the application factory and database instance from the app package
from app import create_app, db
# Import specific models to interact with the database tables
from app.models import Category, Product

# Initialize the Flask application using the factory function
app = create_app()

def seed_database():
    """
    Function to initialize the database and populate it with initial data.
    This ensures that the application has some categories and products
    to display upon the first run.
    """
    # Create an application context to interact with the database
    with app.app_context():
        # FOR DEVELOPMENT ONLY: Drop all existing tables to start fresh every time
        db.drop_all()
        
        # Create all tables defined in the models
        db.create_all()
        
        print("Seeding database fresh...")
        
        # Create category instances with names and descriptions
        c1 = Category(name='Electronics', description='Gadgets, devices, and accessories.')
        c2 = Category(name='Clothing', description='Apparel for men and women.')
        c3 = Category(name='Home & Kitchen', description='Furniture, appliances, and decor.')
        
        # Add all new categories to the database session
        db.session.add_all([c1, c2, c3])
        # Commit the session to save the categories to the database
        db.session.commit()

        # Create product instances linked to their respective categories using foreign keys
        p1 = Product(title='iPhone 17 Pro', description='Latest 5G smartphone with incredible camera.', price=1000.00, image_file='iPhone17Pro.jpg', category_id=c1.id)
        p2 = Product(title='airpods 3', description='Noise-cancelling over-ear airpods with 40h battery.', price=199.99, image_file='airpods.png', category_id=c1.id)
        p3 = Product(title='Cotton T-Shirt', description='100% Cotton breathable everyday T-shirt.', price=19.99, image_file='shirt.jpg', category_id=c2.id)
        p4 = Product(title='Denim Jeans', description='Classic fit denim jeans, rugged and stylish.', price=49.99, image_file='jeans.jpg', category_id=c2.id)
        p5 = Product(title='Coffee Maker', description='Programmable drip coffee maker for perfect mornings.', price=89.99, image_file='coffee.jpg', category_id=c3.id)
        p6 = Product(title='Blender', description='High-power blender for smoothies and shakes.', price=29.99, image_file='b.jpg', category_id=c3.id)

        # Add all new products to the database session
        db.session.add_all([p1, p2, p3, p4, p5, p6])
        # Commit the session to save the products to the database
        db.session.commit()
        print("Database seeded completely!")

# Execution entry point for the script
if __name__ == '__main__':
    # Seed the database before starting the application
    seed_database()
    # Run the Flask development server with debugging enabled
    app.run(debug=True)

