from flask import request, jsonify, render_template, session, redirect, url_for
from models import db, User, Product, Category, Transaction, TransactionDetail, Payment, InventoryLog
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from sqlalchemy import func



def initialize_routes(app):

    # ---------------- Users ----------------
    @app.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data or 'role' not in data:
            return jsonify({'error': 'username, password, and role are required'}), 400
        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], password=hashed_password, role=data['role'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'})

    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        result = [{'user_id': u.user_id, 'username': u.username, 'role': u.role} for u in users]
        return jsonify(result)

    # --- Admin UI User CRUD ---
    @app.route('/admin/users/add', methods=['POST'])
    def admin_add_user():
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/users/edit', methods=['POST'])
    def admin_edit_user():
        user_id = request.form['user_id']
        username = request.form['username']
        password = request.form.get('password')
        role = request.form['role']
        user = User.query.get(user_id)
        if user:
            user.username = username
            if password:
                user.password = generate_password_hash(password)
            user.role = role
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
    def admin_delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # ---------------- Categories ----------------
    @app.route('/categories', methods=['POST'])
    def create_category():
        data = request.get_json()
        category = Category(category_name=data['category_name'])
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category created'})

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        result = [{'category_id': c.category_id, 'category_name': c.category_name} for c in categories]
        return jsonify(result)

    # --- Admin UI Category CRUD ---
    @app.route('/admin/categories/add', methods=['POST'])
    def admin_add_category():
        category_name = request.form['category_name']
        category = Category(category_name=category_name)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/categories/edit', methods=['POST'])
    def admin_edit_category():
        category_id = request.form['category_id']
        category_name = request.form['category_name']
        category = Category.query.get(category_id)
        if category:
            category.category_name = category_name
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
    def admin_delete_category(category_id):
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # ---------------- Products ----------------
    @app.route('/products', methods=['POST'])
    def create_product():
        data = request.get_json()
        product = Product(
            product_name=data['product_name'],
            category_id=data.get('category_id'),
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            unit=data.get('unit', 'pcs')
        )
        db.session.add(product)
        db.session.commit()
        # Add inventory log for initial stock
        if product.stock_quantity > 0:
            log = InventoryLog(
                product_id=product.product_id,
                change_type='Initial Stock',
                quantity_change=product.stock_quantity,
                remarks='Product created with initial stock',
                current_stock=product.stock_quantity
            )
            db.session.add(log)
            db.session.commit()
        return jsonify({'message': 'Product created'})

    @app.route('/products', methods=['GET'])
    def get_products():
        products = Product.query.all()
        result = []
        for p in products:
            result.append({
                'product_id': p.product_id,
                'product_name': p.product_name,
                'category_id': p.category_id,
                'price': p.price,
                'stock_quantity': p.stock_quantity,
                'unit': p.unit
            })
        return jsonify(result)

    # --- Admin UI Product CRUD ---
    @app.route('/admin/products/add', methods=['POST'])
    def admin_add_product():
        product_name = request.form['product_name']
        category_id = request.form['category_id']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']
        unit = request.form['unit']
        product = Product(
            product_name=product_name,
            category_id=category_id,
            price=price,
            stock_quantity=stock_quantity,
            unit=unit
        )
        db.session.add(product)
        db.session.commit()
        # Add inventory log for initial stock
        if int(stock_quantity) > 0:
            log = InventoryLog(
                product_id=product.product_id,
                change_type='Initial Stock',
                quantity_change=int(stock_quantity),
                remarks='Product created with initial stock',
                current_stock=product.stock_quantity
            )
            db.session.add(log)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/products/edit', methods=['POST'])
    def admin_edit_product():
        product_id = request.form['product_id']
        product = Product.query.get(product_id)
        if product:
            product.product_name = request.form['product_name']
            product.category_id = request.form['category_id']
            product.price = request.form['price']
            product.stock_quantity = request.form['stock_quantity']
            product.unit = request.form['unit']
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
    def admin_delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # ---------------- Transactions ----------------
    @app.route('/transactions', methods=['POST'])
    def create_transaction():
        data = request.get_json()
        # --- Add validation ---
        if not data or 'user_id' not in data or 'payment_method' not in data or 'total_amount' not in data or 'items' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return jsonify({'error': 'Items must be a non-empty list'}), 400
        # --- End validation ---
        try:
            transaction = Transaction(
                user_id=data['user_id'],
                payment_method=data['payment_method'],
                total_amount=data['total_amount']
            )
            db.session.add(transaction)
            db.session.commit()

            for item in data['items']:
                # Validate item fields
                if 'product_id' not in item or 'quantity' not in item or 'price' not in item:
                    return jsonify({'error': 'Each item must have product_id, quantity, and price'}), 400
                detail = TransactionDetail(
                    transaction_id=transaction.transaction_id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=item['price'],
                    subtotal=item['quantity'] * item['price']
                )
                db.session.add(detail)
                product = Product.query.get(item['product_id'])
                if not product:
                    return jsonify({'error': f"Product ID {item['product_id']} not found"}), 400
                if product.stock_quantity < item['quantity']:
                    return jsonify({'error': f"Not enough stock for product {product.product_name}"}), 400
                product.stock_quantity -= item['quantity']
                # Add inventory log for deduction
                log = InventoryLog(
                    product_id=product.product_id,
                    change_type='Sale',
                    quantity_change=-item['quantity'],
                    remarks=f'Sold {item["quantity"]} during transaction {transaction.transaction_id}',
                    current_stock=product.stock_quantity
                )
                db.session.add(log)
            db.session.commit()

            payment = Payment(
                transaction_id=transaction.transaction_id,
                method=data['payment_method'],
                amount=data['total_amount']
            )
            db.session.add(payment)
            db.session.commit()

            return jsonify({'message': 'Transaction created successfully', 'transaction_id': transaction.transaction_id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/transactions', methods=['GET'])
    def get_transactions():
        transactions = Transaction.query.all()
        users = User.query.filter(User.role.in_(["admin", "cashier"])).all() # added

        result = []
        for t in transactions:
            items = []
            for d in t.details:
                items.append({
                    'product_id': d.product_id,
                    'quantity': d.quantity,
                    'price': d.price,
                    'subtotal': d.subtotal
                })
            result.append({
                'transaction_id': t.transaction_id,
                'user_id': t.user_id,
                'payment_method': t.payment_method,
                'total_amount': t.total_amount,
                'date_time': t.date_time,
                'items': items
            })
        return jsonify(result)

    # ---------------- Inventory Logs ----------------
    @app.route('/inventory', methods=['POST'])
    def add_inventory_log():
        data = request.get_json()

        # Find product first
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Update product's stock
        product.stock_quantity = (product.stock_quantity or 0) + data['quantity_change']

        # Create log entry
        log = InventoryLog(
            product_id=data['product_id'],
            change_type=data['change_type'],
            quantity_change=data['quantity_change'],
            remarks=data.get('remarks', ''),
            current_stock=product.stock_quantity  # snapshot after update
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({'message': 'Inventory log added'})

    @app.route('/inventory', methods=['GET'])
    def get_inventory_logs():
        logs = InventoryLog.query.all()
        result = []
        for l in logs:
            result.append({
                'log_id': l.log_id,
                'product_id': l.product_id,
                'product_name': l.product.product_name if l.product else None,
                'change_type': l.change_type,
                'quantity_change': l.quantity_change,
                'remarks': l.remarks,
                'date_time': l.date_time,
                'current_stock': l.current_stock 
            })
        return jsonify(result)

    # --- Admin UI InventoryLog CRUD ---
    @app.route('/admin/inventory/edit', methods=['POST'])
    def admin_edit_inventory_log():
        log_id = request.form['log_id']
        product_id = int(request.form['product_id'])
        change_type = request.form['change_type']
        quantity_change = int(request.form['quantity_change'])
        remarks = request.form.get('remarks', '')
        log = InventoryLog.query.get(log_id)
        if log:
            # Adjust product stock based on previous log value
            product = Product.query.get(log.product_id)
            if product:
                product.stock_quantity -= log.quantity_change
            # Update log fields
            log.product_id = product_id
            log.change_type = change_type
            log.quantity_change = quantity_change
            log.remarks = remarks
            # Adjust product stock for new value
            product = Product.query.get(product_id)
            if product:
                product.stock_quantity += quantity_change
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/inventory/delete/<int:log_id>', methods=['POST'])
    def admin_delete_inventory_log(log_id):
        log = InventoryLog.query.get(log_id)
        if log:
            product = Product.query.get(log.product_id)
            if product:
                product.stock_quantity -= log.quantity_change
            db.session.delete(log)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # ---------------- Reports ----------------
    @app.route('/reports/daily', methods=['GET'])
    def daily_report():
        today = date.today()
        transactions = Transaction.query.filter(db.func.date(Transaction.date_time) == today).all()
        total_sales = sum([t.total_amount for t in transactions])
        return jsonify({'date': str(today), 'total_sales': total_sales, 'transactions': len(transactions)})

    @app.route('/reports/monthly', methods=['GET'])
    def monthly_report():
        today = date.today()
        month = today.month
        year = today.year
        transactions = Transaction.query.filter(
            db.extract('month', Transaction.date_time) == month,
            db.extract('year', Transaction.date_time) == year
        ).all()
        total_sales = sum([t.total_amount for t in transactions])
        return jsonify({'month': month, 'year': year, 'total_sales': total_sales, 'transactions': len(transactions)})

    # ---------------- Admin Dashboard ----------------
    @app.route('/admin')
    def admin_dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        users = User.query.all()
        products = Product.query.all()
        transactions = Transaction.query.all()
        inventory_logs = InventoryLog.query.all()
        categories = Category.query.all()
        transaction_details = TransactionDetail.query.all()
        payments = Payment.query.all()

        # existing reports / summary cards
        low_stock = Product.query.filter(Product.stock_quantity < 5).all()
        from sqlalchemy import func
        from datetime import date
        today = date.today()
        top_products = db.session.query(
            Product.product_name,
            func.sum(TransactionDetail.quantity)
        ).join(TransactionDetail, Product.product_id == TransactionDetail.product_id
        ).group_by(Product.product_id
        ).order_by(func.sum(TransactionDetail.quantity).desc()
        ).limit(10).all()
        daily_sales = db.session.query(func.sum(Transaction.total_amount)).filter(db.func.date(Transaction.date_time) == today).scalar() or 0
        month = today.month
        year = today.year
        monthly_sales = db.session.query(func.sum(Transaction.total_amount)).filter(
            db.extract('month', Transaction.date_time) == month,
            db.extract('year', Transaction.date_time) == year
        ).scalar() or 0

        return render_template(
            'admin.html',
            users=users,
            products=products,
            transactions=transactions,
            inventory_logs=inventory_logs,
            categories=categories,
            transaction_details=transaction_details,
            payments=payments,
            low_stock=low_stock,
            top_products=top_products,
            daily_sales=daily_sales,
            monthly_sales=monthly_sales
        )

    #------------------------------------------------------
    # Secret key for session
    app.secret_key = 'your-secret-key'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.user_id
                session['role'] = user.role  # Optionally store role in session
                return redirect(url_for('admin_dashboard'))
            return "Invalid credentials", 401
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))