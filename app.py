from flask import Flask, request, jsonify
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Product, InventoryLog, User
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

# 🔑 Register new user (Admin/Cashier)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if not username or not password or not role:
        return jsonify({"message": "Username, password, and role are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pw, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User '{username}' registered successfully as {role}!"}), 201

# 🔑 Login (Admin/Cashier)
@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({
        "message": f"Welcome {user.role}!",
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role
    }), 200

# 📦 Add product
@app.route('/api/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    category_id = request.form['category_id']
    price = float(request.form['price'])
    stock_quantity = int(request.form['stock_quantity'])
    unit = request.form['unit']

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

    return jsonify({"message": "Product added successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
