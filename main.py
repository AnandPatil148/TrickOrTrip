import tkinter as tk
from tkinter import ttk, messagebox
import dbm, hashlib
import db

USER_DB = "users.db"
PRODUCT_DB = "products.db"

current_user = {"role": None, "username": None}
cart = []

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def signup():
    uname = signup_uname.get()
    pw = signup_pw.get()
    role = user_role.get()
    
    if uname and pw and role:
        with dbm.open(USER_DB, "c") as db:
            if uname in db:
                messagebox.showerror("Error", "Username taken")
                return
            db[uname] = f"{hash_pw(pw)}|{role}"
        messagebox.showinfo("Signup", "Signup successful!")
        show_login()
    else:
        messagebox.showerror("Error", "Complete all fields")

def login():
    uname = login_uname.get()
    pw = login_pw.get()
    with dbm.open(USER_DB, "c") as db:
        if uname in db:
            hpw, role = db[uname].decode().split("|")
            if hpw == hash_pw(pw):
                current_user["role"] = role
                current_user["username"] = uname
                messagebox.showinfo("Login", f"Welcome {role}: {uname}")
                show_main_menu()
                return
    messagebox.showerror("Error", "Invalid credentials")

def show_signup():
    for w in root.winfo_children(): w.destroy()
    ttk.Label(root, text="Sign Up").pack()
    global signup_uname, signup_pw, user_role
    signup_uname = tk.StringVar()
    signup_pw = tk.StringVar()
    user_role = tk.StringVar()
    ttk.Label(root, text="Username:").pack()
    ttk.Entry(root, textvariable=signup_uname).pack()
    ttk.Label(root, text="Password:").pack()
    ttk.Entry(root, textvariable=signup_pw, show="*").pack()
    ttk.Label(root, text="Role:").pack()
    ttk.Radiobutton(root, text="Customer", variable=user_role, value="customer").pack()
    ttk.Radiobutton(root, text="Seller", variable=user_role, value="seller").pack()
    ttk.Button(root, text="Sign Up", command=signup).pack()
    ttk.Button(root, text="Go to Login", command=show_login).pack()

def show_login():
    for w in root.winfo_children(): w.destroy()
    ttk.Label(root, text="Login").pack()
    global login_uname, login_pw
    login_uname = tk.StringVar()
    login_pw = tk.StringVar()
    ttk.Label(root, text="Username:").pack()
    ttk.Entry(root, textvariable=login_uname).pack()
    ttk.Label(root, text="Password:").pack()
    ttk.Entry(root, textvariable=login_pw, show="*").pack()
    ttk.Button(root, text="Login", command=login).pack()
    ttk.Button(root, text="Sign Up", command=show_signup).pack()

def show_main_menu():
    for w in root.winfo_children(): w.destroy()
    role = current_user["role"]
    ttk.Label(root, text=f"Welcome, {role}!").pack()
    if role == "seller":
        ttk.Button(root, text="Upload Product", command=show_upload_product).pack()
    elif role == "customer":
        ttk.Button(root, text="Shop Products", command=show_products).pack()
        ttk.Button(root, text="Cart", command=show_cart).pack()
    ttk.Button(root, text="Logout", command=show_login).pack()

def upload_product():
    name = prod_name.get()
    price = prod_price.get()
    desc = prod_desc.get()
    if name and price and desc:
        with dbm.open(PRODUCT_DB, "c") as db:
            db[name] = f"{price}|{desc}|{current_user['username']}"
        messagebox.showinfo("Upload", "Product Uploaded")
        show_main_menu()
    else:
        messagebox.showerror("Error", "Complete all fields")

def show_upload_product():
    for w in root.winfo_children(): w.destroy()
    global prod_name, prod_price, prod_desc
    ttk.Label(root, text="Upload Product").pack()
    prod_name = tk.StringVar()
    prod_price = tk.StringVar()
    prod_desc = tk.StringVar()
    ttk.Label(root, text="Product Name:").pack()
    ttk.Entry(root, textvariable=prod_name).pack()
    ttk.Label(root, text="Price per Day:").pack()
    ttk.Entry(root, textvariable=prod_price).pack()
    ttk.Label(root, text="Description:").pack()
    ttk.Entry(root, textvariable=prod_desc).pack()
    ttk.Button(root, text="Upload", command=upload_product).pack()
    ttk.Button(root, text="Back", command=show_main_menu).pack()

def add_to_cart():
    sel = [products_listbox.get(i) for i in products_listbox.curselection()]
    for s in sel:
        if s not in cart:
            cart.append(s)
    messagebox.showinfo("Cart", "Added to Cart")

def show_products():
    for w in root.winfo_children(): w.destroy()
    global products_listbox
    ttk.Label(root, text="Select Products").pack()
    products_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60)
    with dbm.open(PRODUCT_DB, "c") as db:
        for key in db.keys():
            name = key.decode()
            price, desc, seller = db[key].decode().split("|")
            products_listbox.insert(tk.END, f"{name} - Rs.{price} - {desc} (By {seller})")
    products_listbox.pack()
    ttk.Button(root, text="Add to Cart", command=add_to_cart).pack()
    ttk.Button(root, text="View Cart", command=show_cart).pack()
    ttk.Button(root, text="Back", command=show_main_menu).pack()

def show_cart():
    for w in root.winfo_children(): w.destroy()
    ttk.Label(root, text="Your Cart").pack()
    cart_listbox = tk.Listbox(root, width=60)
    total = 0
    for item in cart:
        parts = item.split(' - Rs.')
        name = parts[0]
        price = float(parts[1].split(' - ')[0])
        cart_listbox.insert(tk.END, item)
        total += price
    cart_listbox.pack()
    deposit = total * 0.5
    ttk.Label(root, text=f"Total Price: Rs.{total}").pack()
    ttk.Label(root, text=f"Safety Deposit: Rs.{deposit}").pack()
    ttk.Button(root, text="Pay", command=lambda: messagebox.showinfo("Pay", f"Paid Rs.{total+deposit}")).pack()
    ttk.Button(root, text="Back", command=show_main_menu).pack()

root = tk.Tk()
root.title("Tourist Rental Platform")
show_login()
root.mainloop()