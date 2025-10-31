import customtkinter as ctk
from tkinter import messagebox
import dbm, pickle
from PIL import Image, ImageTk

ctk.set_appearance_mode("system")    # "dark", "light", "system"
ctk.set_default_color_theme("blue")  # choices: "blue", "green", "dark-blue"

COMPANY = "TrickOrTrip"
LOGO_PATH = r"D:\TrickOrTrip\logo.jpg"
BACK_PATH = r"D:\TrickOrTrip\backbutton.jpg"
CITIES = ["Bangalore", "Hyderabad", "Chennai"]

USERDB = "users.db"
SELLERDB = "sellers.db"
PRODUCTDB = "products.db"

root = ctk.CTk()
root.title(COMPANY)
root.geometry("880x600")
root.resizable(False, False)

def load_img(path, size):
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)

logo_img = load_img(LOGO_PATH, (120,120))
back_img = load_img(BACK_PATH, (38,38))

frames = {k: ctk.CTkFrame(root) for k in [
    "welcome", "role", "signup", "login", "seller_menu", "seller_products", "product_upload",
    "customer_city", "customer_menu", "search", "all_products", "cart"
]}

page_stack = []
cart = []
user = {"id": None, "role": None, "city": None, "name": None, "email": None}

def store(dbfile, key, value):
    with dbm.open(dbfile, "c") as db:
        db[key] = pickle.dumps(value)

def retrieve(dbfile, key):
    with dbm.open(dbfile, "c") as db:
        v = db.get(key, b"")
        try:
            return pickle.loads(v)
        except Exception:
            return None

def all_items(dbfile):
    items = []
    with dbm.open(dbfile, "c") as db:
        for k in db.keys():
            v = db[k]
            try:
                items.append(pickle.loads(v))
            except Exception:
                continue
    return items

def gen_id(dbfile):
    with dbm.open(dbfile, "c") as db:
        return str(len(db))

def show_frame(name):
    for f in frames.values(): f.pack_forget()
    frames[name].pack(fill="both", expand=True)
    page_stack.append(name)

def go_back():
    if len(page_stack) > 1:
        frames[page_stack.pop()].pack_forget()
        frames[page_stack[-1]].pack(fill="both", expand=True)

def welcome_page():
    f = frames["welcome"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="", image=logo_img, width=120, height=120).pack(pady=20)
    ctk.CTkLabel(f, text=COMPANY, text_color="#800080", font=("Arial",36,"bold")).pack(pady=8)
    enter_btn = ctk.CTkButton(f, text="Enter", command=lambda: show_login_signup())
    enter_btn.pack(pady=56)
    f.pack()

def show_login_signup():
    f = frames["role"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="", image=logo_img).pack(pady=8)
    ctk.CTkLabel(f, text=COMPANY, text_color="#800080", font=("Arial",36,"bold")).pack()
    signup_btn = ctk.CTkButton(f, text="Sign Up", command=lambda: signup_page())
    signup_btn.pack(pady=24)
    login_btn = ctk.CTkButton(f, text="Login", command=lambda: login_page())
    login_btn.pack(pady=24)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=lambda: [go_back(), welcome_page()])
    back_btn.pack(pady=24)
    show_frame("role")

def signup_page():
    show_frame("signup")
    f = frames["signup"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="", image=logo_img).pack(pady=4)
    ctk.CTkLabel(f, text=COMPANY, text_color="#800080", font=("Arial",22,"bold")).pack()
    role = ctk.StringVar(value="customer")
    ctk.CTkLabel(f, text="Role").pack()
    ctk.CTkRadioButton(f, text="Customer", variable=role, value="customer").pack()
    ctk.CTkRadioButton(f, text="Seller", variable=role, value="seller").pack()
    name = ctk.StringVar(); phone = ctk.StringVar(); ar = ctk.StringVar(); city = ctk.StringVar(value=CITIES[0])
    email = ctk.StringVar(); idproof = ctk.StringVar(); pwd = ctk.StringVar()
    ctk.CTkLabel(f, text="Name").pack(); ctk.CTkEntry(f, textvariable=name).pack()
    ctk.CTkLabel(f, text="Phone").pack(); ctk.CTkEntry(f, textvariable=phone).pack()
    ctk.CTkLabel(f, text="Email").pack(); ctk.CTkEntry(f, textvariable=email).pack()
    ctk.CTkLabel(f, text="Password").pack(); ctk.CTkEntry(f, textvariable=pwd, show="*").pack()
    if role.get()=="customer":
        ctk.CTkLabel(f, text="ID Proof").pack(); ctk.CTkEntry(f, textvariable=idproof).pack()
    else:
        ctk.CTkLabel(f, text="Area").pack(); ctk.CTkEntry(f, textvariable=ar).pack()
        ctk.CTkLabel(f, text="City").pack(); ctk.CTkComboBox(f, values=CITIES, variable=city).pack()
    def submit():
        if not (name.get() and phone.get() and email.get() and pwd.get()):
            messagebox.showerror("Err", "Fill all fields"); return
        uid = gen_id(USERDB) if role.get()=="customer" else gen_id(SELLERDB)
        if role.get()=="customer":
            entry = {"id": uid, "role":"customer", "name":name.get(), "phone":phone.get(), "email":email.get(),
                     "idproof":idproof.get(), "pwd":pwd.get(), "city": ""}
            with dbm.open(USERDB, "c") as db: db[email.get()] = pickle.dumps(entry)
        else:
            entry = {"id": uid, "role":"seller", "name":name.get(), "phone":phone.get(), "area":ar.get(), "city":city.get(),
                     "email":email.get(), "pwd":pwd.get()}
            with dbm.open(SELLERDB, "c") as db: db[email.get()] = pickle.dumps(entry)
        messagebox.showinfo("Signup", "Account created!"); go_back()
    submit_btn = ctk.CTkButton(f, text="Submit", command=submit)
    submit_btn.pack(pady=10)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack(pady=10)

def login_page():
    show_frame('login')
    f = frames["login"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="", image=logo_img).pack(pady=8)
    ctk.CTkLabel(f, text=COMPANY, text_color="#800080", font=("Arial",28,"bold")).pack()
    email = ctk.StringVar(); pwd = ctk.StringVar()
    ctk.CTkLabel(f, text="Email").pack(); ctk.CTkEntry(f, textvariable=email).pack()
    ctk.CTkLabel(f, text="Password").pack(); ctk.CTkEntry(f, textvariable=pwd, show="*").pack()
    def do_login():
        entry = None
        for dbfile in [USERDB, SELLERDB]:
            try:
                with dbm.open(dbfile, "c") as db:
                    if email.get() in db:
                        v = db[email.get()]
                        try: entry = pickle.loads(v)
                        except Exception: entry=None
            except Exception: entry=None
        if entry and (entry.get("pwd")==pwd.get()):
            user.update(entry)
            user['email'] = entry.get('email')
            if entry["role"]=="seller": seller_menu()
            else: customer_city_page()
        else:
            messagebox.showerror("Err", "Login Failed")
    login_btn = ctk.CTkButton(f, text="Login", command=do_login)
    login_btn.pack(pady=10)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack(pady=8)

def seller_menu():
    show_frame('seller_menu')
    f=frames["seller_menu"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="", image=logo_img).pack(pady=8)
    ctk.CTkLabel(f, text=COMPANY, text_color="#800080", font=("Arial",24,"bold")).pack()
    upload_btn = ctk.CTkButton(f, text="Upload Product", command=product_upload)
    upload_btn.pack(pady=10)
    view_btn = ctk.CTkButton(f, text="View Products", command=seller_products_page)
    view_btn.pack(pady=8)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack()

def product_upload():
    show_frame('product_upload')
    f=frames["product_upload"]
    for w in f.winfo_children(): w.destroy()
    name=ctk.StringVar(); price=ctk.StringVar(); tags=ctk.StringVar()
    ctk.CTkLabel(f, text="Name").pack(); ctk.CTkEntry(f, textvariable=name).pack()
    ctk.CTkLabel(f, text=f"Price (Rs/day) [{user['city']}]").pack(); ctk.CTkEntry(f, textvariable=price).pack()
    ctk.CTkLabel(f, text="Tags (comma separated)").pack(); ctk.CTkEntry(f, textvariable=tags).pack()
    def submit():
        pid = gen_id(PRODUCTDB)
        entry = {"id":pid, "seller_id":user['id'], "name":name.get(), "price":float(price.get()),
                 "tags":tags.get(), "city":user['city'], "rented":0}
        store(PRODUCTDB, pid, entry)
        messagebox.showinfo("Success", "Uploaded"); go_back()
    upload_btn = ctk.CTkButton(f, text="Upload", command=submit)
    upload_btn.pack(pady=8)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack()

def seller_products_page():
    show_frame('seller_products')
    f=frames["seller_products"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="Your Products").pack()
    listbox = ctk.CTkTextbox(f, width=600, height=380)
    listbox.pack(pady=5)
    for prod in all_items(PRODUCTDB):
        if prod and prod.get("seller_id")==user["id"] and prod.get("city")==user["city"]:
            status = 'RENTED' if prod['rented'] else 'Available'
            line = f"{prod['name']} | Rs.{prod['price']} | {prod['tags']} | {status}\n"
            listbox.insert("end", line)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack(pady=12)

def customer_city_page():
    show_frame("customer_city")
    f=frames["customer_city"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f,text="", image=logo_img).pack()
    ctk.CTkLabel(f,text=COMPANY, text_color="#800080", font=("Arial",24,"bold")).pack()
    ctk.CTkLabel(f, text="Select City").pack()
    city=ctk.StringVar(value=CITIES[0])
    city_box = ctk.CTkComboBox(f, values=CITIES, variable=city)
    city_box.pack()
    continue_btn = ctk.CTkButton(f, text="Continue", command=lambda: [user.update({"city":city.get()}), customer_menu()])
    continue_btn.pack(pady=10)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack(pady=8)

def customer_menu():
    show_frame("customer_menu")
    f=frames["customer_menu"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f,text="", image=logo_img).pack()
    ctk.CTkLabel(f,text=COMPANY, text_color="#800080", font=("Arial",24,"bold")).pack()
    view_btn = ctk.CTkButton(f, text="View All Products", command=customer_all_products_page)
    view_btn.pack(pady=6)
    search_btn = ctk.CTkButton(f, text="Search Products", command=search_page)
    search_btn.pack(pady=6)
    cart_btn = ctk.CTkButton(f, text="Cart/Checkout", command=cart_page)
    cart_btn.pack(pady=8)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack()

def customer_all_products_page():
    show_frame("all_products")
    f = frames["all_products"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text=f"Products available in {user['city']}", font=("Arial",18)).pack()
    # --- Use tk.Listbox for selection ---
    import tkinter as tk  # local import, no conflict
    lb = tk.Listbox(f, selectmode=tk.MULTIPLE, width=110, height=20, bg="#fff6fd", fg="#50214f", font=("Segoe UI", 12), highlightthickness=2, highlightbackground="#e07aef")
    lb.pack()
    products = []
    for prod in all_items(PRODUCTDB):
        if prod and prod.get("city")==user["city"] and not prod.get("rented"):
            seller = "Unknown"
            for s in all_items(SELLERDB):
                if s and s.get("id")==prod.get("seller_id"):
                    seller = s.get("name")
            prodline = f"{prod['id']}|{prod['name']} | Rs.{prod['price']} | {prod['tags']} | Seller:{seller}"
            products.append(prodline)
            lb.insert(tk.END, prodline)
    ctk.CTkLabel(f, text="Days to Rent:").pack()
    days = ctk.StringVar()
    ctk.CTkEntry(f, textvariable=days).pack()
    def add_to_cart():
        selected = [lb.get(i) for i in lb.curselection()]
        if not selected or not days.get().isdigit():
            messagebox.showerror("Error", "Select products and enter valid days."); return
        for prodline in selected:
            pid, name, rest = prodline.split("|",2)
            price = float(rest.split("Rs.")[1].split(" ")[0])
            cart.append({"pid":pid.strip(), "name":name.strip(), "price":price, "days":int(days.get())})
        messagebox.showinfo("Cart", "Added to cart")
    def rent_now():
        add_to_cart()
        cart_page()
    rent_btn = ctk.CTkButton(f, text="Rent Now", command=rent_now)
    rent_btn.pack(pady=6)
    cart_btn = ctk.CTkButton(f, text="Add to Cart", command=add_to_cart)
    cart_btn.pack(pady=6)
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack(pady=8)


def search_page():
    show_frame("search")
    f=frames["search"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f, text="Search Products").pack()
    search=ctk.StringVar(); days=ctk.StringVar()
    ctk.CTkEntry(f,textvariable=search).pack()
    ctk.CTkLabel(f,text="Days").pack()
    ctk.CTkEntry(f,textvariable=days).pack()
    lb=ctk.CTkTextbox(f, width=700, height=140)
    lb.pack()
    def query():
        lb.delete("1.0","end")
        q=search.get().lower()
        found = False
        for prod in all_items(PRODUCTDB):
            if prod and prod.get("city")==user["city"] and not prod.get("rented"):
                match = (q in prod["name"].lower() or q in prod["tags"].lower())
                if match:
                    line = f"{prod['id']}|{prod['name']}|{prod['price']}|{prod['tags']}\n"
                    lb.insert("end", line)
                    found = True
        if not found:
            lb.insert("end", "item not found\n")
    search_btn = ctk.CTkButton(f, text="Search", command=query)
    search_btn.pack()
    def pick(addcart):
        items = lb.get("1.0","end").splitlines()
        items = [it for it in items if it != "item not found" and it.strip()]
        if not items or not days.get().isdigit(): 
            messagebox.showerror("Err", "Choose items and enter valid days")
            return
        d=int(days.get())
        for item in items:
            pid,name,price,tag=item.split("|")
            cart.append({"pid":pid, "name":name, "price":float(price), "days":d})
        if addcart: messagebox.showinfo("Cart", "Added")
        else: cart_page()
    rent_btn = ctk.CTkButton(f, text="Rent Now", command=lambda: pick(False))
    rent_btn.pack()
    add_btn = ctk.CTkButton(f, text="Add to Cart", command=lambda: pick(True))
    add_btn.pack()
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack()

def cart_page():
    show_frame("cart")
    f=frames["cart"]
    for w in f.winfo_children(): w.destroy()
    ctk.CTkLabel(f,text="Your Cart").pack()
    lb=ctk.CTkTextbox(f, width=760, height=120)
    total=0
    for item in cart:
        txt=f"{item['name']} | {item['price']} x {item['days']}\n"
        lb.insert("end", txt)
        total+=item["price"]*item["days"]
    lb.pack()
    deposit=min(total*0.5, 10000)
    ctk.CTkLabel(f, text=f"Total: Rs.{total}").pack()
    ctk.CTkLabel(f, text=f"Safety Deposit: Rs.{deposit} (max 10,000)").pack()
    def pay():
        for item in cart:
            prod = retrieve(PRODUCTDB, item["pid"])
            if prod:
                prod["rented"]=1
                store(PRODUCTDB, item["pid"], prod)
        cart.clear()
        messagebox.showinfo("Paid", "Rental complete!"); go_back()
    pay_btn = ctk.CTkButton(f, text="Checkout/Pay", command=pay)
    pay_btn.pack()
    back_btn = ctk.CTkButton(f, image=back_img, text="", command=go_back)
    back_btn.pack()

welcome_page()
root.mainloop()





