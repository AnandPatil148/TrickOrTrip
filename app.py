from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib, os
import db

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "main.db"

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

@app.route('/')
def home():
    # if 'user' in session:
    #     if session['user']['role'] == 'seller':
    #         return redirect(url_for('dashboard'))
    #     elif session['user']['role'] == 'customer':
    #         return redirect(url_for('shop'))
    products = db.get_recent_gear(DB_NAME, limit=4)
    return render_template('home.html', products=products, user=session.get('user'))


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if 'user' in session:
            return redirect(url_for('dashboard'))
        username = request.form['username']
        phone = request.form['phone']
        email = request.form['email']
        pw = request.form['password']
        role = request.form.get('role')

        if not all([username, phone, email, pw, role]):
            flash("Please fill all fields!", "error")
            return redirect(url_for('signup'))

        if role == "seller":
            if db.get_seller(DB_NAME, email):
                flash("Seller already exists!", "error")
                return redirect(url_for('signup'))
            db.insert_seller(DB_NAME, username, phone, email, hash_pw(pw))
        else:
            if db.get_customer(DB_NAME, email):
                flash("Customer already exists!", "error")
                return redirect(url_for('signup'))
            db.insert_customer(DB_NAME, username, phone, email, hash_pw(pw))

        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'user' in session:
            return redirect(url_for('dashboard'))
        
        email = request.form.get('email', '').strip()
        pw = request.form.get('password', '')

        if not email or not pw:
            flash("Enter email and password.", "error")
            return render_template('login.html')

        hashed = hash_pw(pw)
        # print(f"{email} / {hashed}")

        # No role given — try both tables and pick the one that matches the password
        seller = db.get_seller(DB_NAME, email)
        customer = db.get_customer(DB_NAME, email)
        
        # If neither matched on password, we'll still set user to whichever exists
        # so we can give a clearer message below
        user = seller or customer
        role = "seller" if seller else ("customer" if customer else None)

        # Final check: user must exist and stored password must match
        if user and role and user[5] == hashed:
            session['user'] = {
                "id": user[0],
                "username": user[1],
                "email": email,
                "role": role
            }
            flash(f"Welcome {user[1]}!", "success")
            
            if role == "customer":
                return redirect(url_for('shop'))
            
            return redirect(url_for('dashboard'))
        else:
            # Helpful error messages:
            if user is None:
                flash("No account found with that email.", "error")
            else:
                flash("Invalid password for the chosen account.", "error")
            return render_template('login.html')

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

# ---------------- UPLOAD (SELLER) ----------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session or session['user']['role'] != 'seller':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        gear_name = request.form['gear_name']
        category = request.form['category']
        price_per_day = request.form['price_per_day']
        security_deposit = request.form['security_deposit']
        quantity = request.form['quantity']
        description = request.form['description']

        if not all([gear_name, category, price_per_day, security_deposit, quantity, description]):
            flash("Please fill all fields!", "error")
            return redirect(url_for('upload'))

        db.insert_gear(
            DB_NAME,
            session['user']['id'],
            session['user']['username'],
            gear_name,
            category,
            price_per_day,
            security_deposit,
            quantity,
            description
        )

        flash("Gear uploaded successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('upload.html')


# ---------------- SHOP (CUSTOMER) ----------------
@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if 'user' not in session:
        return redirect(url_for('login'))

    # products = db.get_all_gear(DB_NAME)
    
    search_query = request.args.get('search', '').strip()

    if search_query:
        products = db.search_gear(DB_NAME, search_query)
    else:
        products = db.get_all_gear(DB_NAME)
        print(products)
        

    if request.method == 'POST':
        pid = request.form['pid']
        session.setdefault('cart', [])
        if pid not in session['cart']:
            session['cart'].append(pid)
        session.modified = True
        flash("Added to cart!", "success")

    return render_template('shop.html', products=products)

# ---------------- CART ----------------
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    session.setdefault('cart', [])

    # 🧹 Handle item removal
    if request.method == 'POST' and 'remove_pid' in request.form:
        pid = request.form['remove_pid']
        if pid in session['cart']:
            session['cart'].remove(pid)
            session.modified = True
            flash("Item removed from cart.", "info")
        return redirect(url_for('cart'))

    # 🛒 Fetch items
    products = db.get_gear_by_ids(DB_NAME, session['cart'])
    total = sum([p[4] for p in products]) if products else 0  # p[4] = price_per_day
    deposit = total * 0.5

    return render_template('cart.html', products=products, total=total, deposit=deposit)


@app.route('/my_products')
def my_products():
    if 'user' not in session or session['user']['role'] != 'seller':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    seller_id = session['user']['id']
    products = db.get_gear_by_seller(DB_NAME, seller_id)

    return render_template('my_products.html', products=products)

@app.route('/edit_products/<int:pid>', methods=['GET', 'POST'])
def edit_product(pid):
    if 'user' not in session or session['user']['role'] != 'seller':
        flash("Unauthorized access.", "error")
    
        return redirect(url_for('login'))

    if request.method == 'POST':
        gear_name = request.form['gear_name']
        category = request.form['category']
        price_per_day = request.form['price_per_day']
        security_deposit = request.form['security_deposit']
        quantity = request.form['quantity']
        description = request.form['description']
        
        
        
        if not all([gear_name, category, price_per_day, security_deposit, quantity, description]):
            flash("Please fill all fields!", "error")
            return redirect(url_for('edit_product', pid=pid))

        db.update_gear(DB_NAME, pid, gear_name, category, price_per_day, security_deposit, quantity, description)
        flash("Product updated successfully!", "success")
        return redirect(url_for('my_products'))

    product = db.get_gear_by_ids(DB_NAME, [pid])
    default = db.get_gear_by_ids(DB_NAME, [pid])[0]
    print(default)
    return render_template('edit_product.html', product=product, default=default)    

@app.route('/payment_success', methods=['POST'])
def payment_success():
    if 'user' not in session or session['user']['role'] != 'customer':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    user = session['user']
    cart_items = session.get('cart', [])

    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for('cart'))

    # 🧾 Record rentals
    for gear_id in cart_items:
        gear = db.get_gear_by_id(DB_NAME, gear_id)
        if not gear:
            continue

        gear_name = gear[2]
        price_per_day = gear[4]

        # You can add start_date and end_date logic here later
        db.insert_rental(DB_NAME, user['id'], gear_id, gear_name, price_per_day)

        # Mark gear as unavailable
        db.update_gear_availability(DB_NAME, gear_id, False)

    # Clear cart
    session['cart'] = []
    session.modified = True

    flash("Payment successful! Rentals confirmed.", "success")
    return redirect(url_for('rentals_success'))

@app.route('/rentals_success')
def rentals_success():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('payment_success.html')

@app.route('/my_rentals')
def my_rentals():
    if 'user' not in session or session['user']['role'] != 'customer':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    user = session['user']
    rentals = db.get_rentals_by_customer(DB_NAME, user['id'])

    return render_template('my_rentals.html', rentals=rentals)
    

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# ---------------- MAIN ----------------
if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        db.create_db(DB_NAME)
    app.run(host="0.0.0.0", port=5000, debug=True)
