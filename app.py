from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    sales_channel = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'd' and password == 'd':
            session['logged_in'] = True
            flash('You were successfully logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        search_term = request.form.get('search')
        orders = Order.query.filter(
            (Order.customer_name.contains(search_term)) |
            (Order.product.contains(search_term)) |
            (Order.sales_channel.contains(search_term))
        ).all()
    else:
        orders = Order.query.all()
        
    return render_template('dashboard.html', orders=orders)
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if not session.get('logged_in'):
        flash('You need to be logged in to add an order', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        product = request.form.get('product')
        sales_channel = request.form.get('sales_channel')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        new_order = Order(customer_name=customer_name, product=product, sales_channel=sales_channel, date=date)
        db.session.add(new_order)
        db.session.commit()
        flash('Order added successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_order.html')

@app.route('/shopping_list')
def shopping_list():
    if not session.get('logged_in'):
        flash('You need to be logged in to view the shopping list', 'danger')
        return redirect(url_for('login'))
    items = ShoppingList.query.all()
    return render_template('shopping_list.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if not session.get('logged_in'):
        flash('You need to be logged in to add an item', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        product = request.form.get('product')
        supplier = request.form.get('supplier')
        new_item = ShoppingList(product=product, supplier=supplier)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully', 'success')
        return redirect(url_for('shopping_list'))
    return render_template('add_item.html')

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if not session.get('logged_in'):
        flash('You need to be logged in to edit an order', 'danger')
        return redirect(url_for('login'))
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        order.customer_name = request.form.get('customer_name')
        order.product = request.form.get('product')
        order.sales_channel = request.form.get('sales_channel')
        order.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        db.session.commit()
        flash('Order updated successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_order.html', order=order)

@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    if not session.get('logged_in'):
        flash('You need to be logged in to delete an order', 'danger')
        return redirect(url_for('login'))
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully', 'success')
    return redirect(url_for('dashboard'))


@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if not session.get('logged_in'):
        flash('You need to be logged in to edit an item', 'danger')
        return redirect(url_for('login'))
    item = ShoppingList.query.get_or_404(item_id)
    if request.method == 'POST':
        item.product = request.form.get('product')
        item.supplier = request.form.get('supplier')
        db.session.commit()
        flash('Item updated successfully', 'success')
        return redirect(url_for('shopping_list'))
    return render_template('edit_item.html', item=item)




@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if not session.get('logged_in'):
        flash('You need to be logged in to delete an item', 'danger')
        return redirect(url_for('login'))
    item = ShoppingList.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully', 'success')
    return redirect(url_for('shopping_list'))



from flask_restful import Resource, Api

api = Api(app)

class OrderResource(Resource):
    def get(self, order_id):
        order = Order.query.get_or_404(order_id)
        return {
            'id': order.id,
            'customer_name': order.customer_name,
            'product': order.product,
            'sales_channel': order.sales_channel,
            'date': order.date.strftime('%Y-%m-%d %H:%M:%S')
        }

class OrderListResource(Resource):
    def get(self):
        orders = Order.query.all()
        return [{
            'id': order.id,
            'customer_name': order.customer_name,
            'product': order.product,
            'sales_channel': order.sales_channel,
            'date': order.date.strftime('%Y-%m-%d %H:%M:%S')
        } for order in orders]

class ShoppingListResource(Resource):
    def get(self, item_id):
        item = ShoppingList.query.get_or_404(item_id)
        return {
            'id': item.id,
            'product': item.product,
            'supplier': item.supplier
        }

class ShoppingListListResource(Resource):
    def get(self):
        items = ShoppingList.query.all()
        return [{
            'id': item.id,
            'product': item.product,
            'supplier': item.supplier
        } for item in items]

api.add_resource(OrderResource, '/api/orders/<int:order_id>')
api.add_resource(OrderListResource, '/api/orders')
api.add_resource(ShoppingListResource, '/api/shopping_list/<int:item_id>')
api.add_resource(ShoppingListListResource, '/api/shopping_list')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
