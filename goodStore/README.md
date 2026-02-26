# goodStore 🛒

A full-stack e-commerce web application built with **Python** and **Flask**. goodStore features a modular codebase, user authentication, a dynamic product catalog, and a functional shopping cart and checkout system.

## 🌟 Features
- **User Authentication:** Secure registration and login using `Flask-Login` and `Flask-Bcrypt`.
- **Product Catalog:** Browse products by categories (Electronics, Clothing, Home & Kitchen).
- **Shopping Cart:** Add, remove, and update product quantities in a session-based active cart.
- **Checkout System:** Convert active carts into finalized orders safely.
- **Auto-Seeding Database:** Automatically wipes and generates dummy products every time the app starts for rapid prototyping and testing.
- **Responsive Design:** Premium UI inspired by modern e-commerce giants using custom CSS variables and flexbox/grid layouts.

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Database:** SQLite (managed via `Flask-SQLAlchemy`)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templating
- **Security:** `Flask-Bcrypt` (Password Hashing)

---

## 🚀 How to Run the Project locally

Follow these steps to get the goodStore application running on your own machine.

### 1. Prerequisites
Make sure you have [Python](https://www.python.org/downloads/) installed on your computer.

### 2. Install Dependencies
Open your terminal (Command Prompt or PowerShell), navigate to the root `goodStore` folder, and install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Flask development server by running the main entry file:

```bash
python run.py
```

### 4. View the App
Once the server is running, open your web browser and go to:
**http://127.0.0.1:5000**

---

### 📝 Note on Database Updates
The `run.py` file is currently configured for rapid development. **Every time you start the server using `python run.py`**, the application will:
1. Delete the old `site.db` database.
2. Recreate all the tables from scratch.
3. Re-seed the database with the dummy products defined in `run.py`.

If you wish to change a product's name, price, or image, simply edit the `Product(...)` lines inside `run.py`, save the file, and restart the python server! To add new photos, place them inside the `app/static/images/` directory.
