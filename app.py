from flask import Flask, request
from flask_migrate import Migrate
from models import db, Product, InventoryLog
from config import Config
from routes import initialize_routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Register all API routes
initialize_routes(app)

@app.route('/')
def index():
    return "POS System API Running ✅"

@app.route('/admin/products/add', methods=['POST'])
def add_product():
    # Get form data
    product_name = request.form['product_name']
    category_id = request.form['category_id']
    price = float(request.form['price'])
    stock_quantity = int(request.form['stock_quantity'])
    unit = request.form['unit']

    # Create product
    new_product = Product(
        product_name=product_name,
        category_id=category_id,
        price=price,
        stock_quantity=stock_quantity,
        unit=unit
    )
    db.session.add(new_product)
    db.session.commit()
    print(f"Product added: {new_product.product_id}")

    # Add inventory log for initial stock
    if stock_quantity > 0:
        log = InventoryLog(
            product_id=new_product.product_id,
            change_type='stock_in',
            quantity_change=stock_quantity,
            remarks='Initial stock on product creation'
        )
        db.session.add(log)
        db.session.commit()
        print(f"Inventory log added: {log.log_id}")

    return "Product added successfully!"

if __name__ == '__main__':
    app.run(debug=True)
