import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import datetime

# ================= DATABASE =================
conn = sqlite3.connect("car_dealership.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Cars (
    CarID INTEGER PRIMARY KEY AUTOINCREMENT,
    CarName TEXT,
    Brand TEXT,
    Price REAL,
    Quantity INTEGER,
    Image TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Invoices (
    InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerName TEXT,
    Date TEXT,
    Total REAL
)
""")

conn.commit()

# ================= GLOBAL =================
image_path = ""
img = None

# ================= FUNCTIONS =================
def load_cars():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM Cars")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row[:5])

def choose_image():
    global image_path
    file = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if file:
        image_path = file
        lbl_img_path.config(text="Đã chọn ảnh")

def add_car():
    global image_path
    name = entry_name.get().strip()
    brand = entry_brand.get().strip()
    price = entry_price.get().strip()
    quantity = entry_quantity.get().strip()

    if not name or not brand or not price or not quantity:
        messagebox.showwarning("Lỗi", "Nhập đầy đủ dữ liệu")
        return

    try:
        price = float(price)
        quantity = int(quantity)
    except:
        messagebox.showerror("Lỗi", "Giá và số lượng phải là số")
        return

    cursor.execute(
        "INSERT INTO Cars (CarName, Brand, Price, Quantity, Image) VALUES (?, ?, ?, ?, ?)",
        (name, brand, price, quantity, image_path)
    )
    conn.commit()
    load_cars()

    entry_name.delete(0, tk.END)
    entry_brand.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    lbl_img_path.config(text="Chưa chọn ảnh")
    image_path = ""

def delete_car():
    selected = tree.selection()
    if not selected:
        return
    car_id = tree.item(selected[0])["values"][0]
    cursor.execute("DELETE FROM Cars WHERE CarID=?", (car_id,))
    conn.commit()
    load_cars()

def update_car():
    selected = tree.selection()
    if not selected:
        return
    car_id = tree.item(selected[0])["values"][0]

    cursor.execute("""
    UPDATE Cars SET CarName=?, Brand=?, Price=?, Quantity=?, Image=? WHERE CarID=?
    """, (
        entry_name.get(),
        entry_brand.get(),
        float(entry_price.get()),
        int(entry_quantity.get()),
        image_path,
        car_id
    ))
    conn.commit()
    load_cars()

def on_select(event):
    global img
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]

        entry_name.delete(0, tk.END)
        entry_name.insert(0, values[1])
        entry_brand.delete(0, tk.END)
        entry_brand.insert(0, values[2])
        entry_price.delete(0, tk.END)
        entry_price.insert(0, values[3])
        entry_quantity.delete(0, tk.END)
        entry_quantity.insert(0, values[4])

        cursor.execute("SELECT Image FROM Cars WHERE CarID=?", (values[0],))
        result = cursor.fetchone()

        if result and result[0]:
            try:
                image = Image.open(result[0])
                image = image.resize((200,150))
                img = ImageTk.PhotoImage(image)
                lbl_image.config(image=img)
            except:
                lbl_image.config(image="")

def search_car():
    keyword = entry_search.get()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM Cars WHERE CarName LIKE ?", ('%' + keyword + '%',))
    for row in cursor.fetchall():
        tree.insert("", "end", values=row[:5])

# ================= GIỎ HÀNG =================
def add_to_cart():
    selected = tree.selection()
    if selected:
        cart_tree.insert("", "end", values=tree.item(selected[0])["values"])

def remove_cart():
    selected = cart_tree.selection()
    if selected:
        cart_tree.delete(selected[0])

def checkout():
    if not cart_tree.get_children():
        messagebox.showwarning("Lỗi", "Giỏ hàng trống")
        return

    total = 0
    for item in cart_tree.get_children():
        total += float(cart_tree.item(item)["values"][3])

    discount = float(entry_discount.get() or 0)
    total -= total * discount / 100

    cursor.execute("""
    INSERT INTO Invoices (CustomerName, Date, Total)
    VALUES (?, ?, ?)
    """, (
        entry_customer.get(),
        datetime.datetime.now().strftime("%Y-%m-%d"),
        total
    ))

    conn.commit()
    cart_tree.delete(*cart_tree.get_children())
    messagebox.showinfo("OK", f"Tổng tiền: {total}")

# ================= UI =================
root = tk.Tk()
root.title("🚗 Car Manager PRO")
root.geometry("1000x600")
root.configure(bg="#1e1e2f")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ===== TAB XE =====
frame_car = tk.Frame(notebook, bg="#1e1e2f")
notebook.add(frame_car, text="Quản lý xe")

form = tk.Frame(frame_car, bg="#2b2b3c")
form.pack(pady=10)

tk.Label(form, text="Tên xe", bg="#2b2b3c", fg="white").grid(row=0, column=0)
entry_name = tk.Entry(form)
entry_name.grid(row=0, column=1)

tk.Label(form, text="Hãng", bg="#2b2b3c", fg="white").grid(row=1, column=0)
entry_brand = tk.Entry(form)
entry_brand.grid(row=1, column=1)

tk.Label(form, text="Giá", bg="#2b2b3c", fg="white").grid(row=2, column=0)
entry_price = tk.Entry(form)
entry_price.grid(row=2, column=1)

tk.Label(form, text="Số lượng", bg="#2b2b3c", fg="white").grid(row=3, column=0)
entry_quantity = tk.Entry(form)
entry_quantity.grid(row=3, column=1)

tk.Button(form, text="Chọn ảnh", command=choose_image).grid(row=4, column=0)
lbl_img_path = tk.Label(form, text="Chưa chọn ảnh", bg="#2b2b3c", fg="white")
lbl_img_path.grid(row=4, column=1)

tk.Button(form, text="Thêm", command=add_car, bg="green", fg="white").grid(row=5, column=0)
tk.Button(form, text="Sửa", command=update_car, bg="blue", fg="white").grid(row=5, column=1)
tk.Button(form, text="Xóa", command=delete_car, bg="red", fg="white").grid(row=5, column=2)

entry_search = tk.Entry(frame_car)
entry_search.pack()
tk.Button(frame_car, text="Search", command=search_car).pack()

tree = ttk.Treeview(frame_car, columns=("ID","Name","Brand","Price","Qty"), show="headings")
for col in ("ID","Name","Brand","Price","Qty"):
    tree.heading(col, text=col)
tree.pack(fill="both", expand=True)

tree.bind("<<TreeviewSelect>>", on_select)

lbl_image = tk.Label(frame_car, bg="#1e1e2f")
lbl_image.pack()

# ===== TAB BÁN =====
frame_sale = tk.Frame(notebook)
notebook.add(frame_sale, text="Bán xe")

tk.Label(frame_sale, text="Khách hàng").pack()
entry_customer = tk.Entry(frame_sale)
entry_customer.pack()

tk.Label(frame_sale, text="Giảm giá (%)").pack()
entry_discount = tk.Entry(frame_sale)
entry_discount.pack()

tk.Button(frame_sale, text="Thêm vào giỏ", command=add_to_cart).pack()
tk.Button(frame_sale, text="Xóa", command=remove_cart).pack()
tk.Button(frame_sale, text="Thanh toán", command=checkout).pack()

cart_tree = ttk.Treeview(frame_sale, columns=("ID","Name","Brand","Price","Qty"), show="headings")
for col in ("ID","Name","Brand","Price","Qty"):
    cart_tree.heading(col, text=col)
cart_tree.pack(fill="both", expand=True)

# LOAD
load_cars()

root.mainloop()