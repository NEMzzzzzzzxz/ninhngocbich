import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton, QLabel,
                             QDialog, QFormLayout, QComboBox, QMessageBox, QLineEdit, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from db_connection import execute_query
from datetime import date

class OrderDialog(QDialog):
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin đơn hàng")
        self.setFixedWidth(400)
        self.layout = QFormLayout(self)

        # Thay vì dùng ComboBox, ta dùng QLineEdit để nhập tên khách hàng trực tiếp
        self.txt_order_id = QLineEdit()
        self.txt_cust_name = QLineEdit() # Ô nhập tên khách hàng mới/tự do
        self.txt_cust_phone = QLineEdit() # Thêm ô nhập SĐT để tạo khách hàng mới
        
        self.cb_car = QComboBox()
        self.cb_emp = QComboBox()
        self.txt_value = QLineEdit()
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Chờ xử lý", "Đang xử lý", "Hoàn thành"])

        self.load_data()

        if order:
            self.txt_order_id.setText(order['order_id'])
            self.txt_order_id.setReadOnly(True)
            self.txt_cust_name.setText(order['customer_name'])
            self.txt_cust_name.setReadOnly(True) # Khi sửa thì không cho đổi tên khách để tránh lỗi liên kết
            self.txt_cust_phone.setVisible(False) # Ẩn ô SĐT khi sửa
            self.cb_car.setCurrentText(order['car_name'])
            self.cb_emp.setCurrentText(order['employee_name'])
            self.txt_value.setText(str(int(order['order_value'])))
            self.cb_status.setCurrentText(order['status'])
        else:
            last = execute_query("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1", fetch=True)
            num = int(last[0]['order_id'][2:]) + 1 if last else 1
            self.txt_order_id.setText(f"HD{num:03d}")

        self.layout.addRow("Mã đơn:", self.txt_order_id)
        self.layout.addRow("Tên khách hàng:", self.txt_cust_name)
        if not order: self.layout.addRow("SĐT khách hàng:", self.txt_cust_phone)
        self.layout.addRow("Chọn xe:", self.cb_car)
        self.layout.addRow("Nhân viên bán:", self.cb_emp)
        self.layout.addRow("Giá trị đơn (VNĐ):", self.txt_value)
        self.layout.addRow("Trạng thái:", self.cb_status)

        btn_save = QPushButton("Lưu đơn hàng")
        btn_save.setStyleSheet("background-color: #2980b9; color: white; height: 30px; font-weight: bold;")
        btn_save.clicked.connect(self.accept)
        self.layout.addRow(btn_save)

    def load_data(self):
        cars = execute_query("SELECT car_id, car_name FROM cars", fetch=True)
        emps = execute_query("SELECT employee_id, full_name FROM employees WHERE status='Đang làm'", fetch=True)
        
        self.car_map = {c['car_name']: c['car_id'] for c in cars}
        self.emp_map = {e['full_name']: e['employee_id'] for e in emps}
        
        self.cb_car.addItems(self.car_map.keys())
        self.cb_emp.addItems(self.emp_map.keys())

    def get_data(self):
        return {
            'order_id': self.txt_order_id.text(),
            'customer_name': self.txt_cust_name.text(),
            'customer_phone': self.txt_cust_phone.text(),
            'car_id': self.car_map.get(self.cb_car.currentText()),
            'employee_id': self.emp_map.get(self.cb_emp.currentText()),
            'order_value': float(self.txt_value.text() or 0),
            'status': self.cb_status.currentText()
        }

class SalesManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý đơn hàng - Auto Pro")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #f5f6fa;")
        
        layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        title = QLabel("DANH SÁCH ĐƠN HÀNG")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        btn_add = QPushButton("+ Tạo đơn hàng")
        btn_add.setStyleSheet("background-color: #27ae60; color: white; padding: 5px 15px;")
        btn_add.clicked.connect(self.add_order)
        
        header.addWidget(title); header.addStretch(); header.addWidget(btn_add)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Mã HD", "Khách hàng", "Xe", "Nhân viên", "Giá trị", "Ngày", "Trạng thái", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.load_orders()

    def load_orders(self):
        query = """
            SELECT o.order_id, cus.full_name AS customer_name, car.car_name, 
                   emp.full_name AS employee_name, o.order_value, o.order_date, o.status,
                   o.customer_id, o.car_id, o.employee_id
            FROM orders o
            LEFT JOIN customers cus ON o.customer_id = cus.customer_id
            LEFT JOIN cars car ON o.car_id = car.car_id
            LEFT JOIN employees emp ON o.employee_id = emp.employee_id
            ORDER BY o.order_date DESC
        """
        self.data = execute_query(query, fetch=True)
        self.render_table()

    def render_table(self):
        self.table.setRowCount(0)
        for row, item in enumerate(self.data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item['order_id']))
            self.table.setItem(row, 1, QTableWidgetItem(str(item['customer_name'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['car_name'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['employee_name'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"{item['order_value']:,.0f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(item['order_date'])))
            
            st_item = QTableWidgetItem(item['status'])
            if item['status'] == "Hoàn thành": st_item.setForeground(QColor("green"))
            self.table.setItem(row, 6, st_item)

            btn_box = QWidget()
            btn_layout = QHBoxLayout(btn_box); btn_layout.setContentsMargins(0,0,0,0)
            
            edit_btn = QPushButton("Sửa")
            edit_btn.clicked.connect(lambda _, r=item: self.edit_order(r))
            del_btn = QPushButton("Xóa")
            del_btn.clicked.connect(lambda _, r=item: self.delete_order(r))
            
            btn_layout.addWidget(edit_btn); btn_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 7, btn_box)

    def add_order(self):
        dlg = OrderDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            
            # BƯỚC 1: Tự động tạo khách hàng mới vào bảng customers
            new_cust = execute_query("INSERT INTO customers (full_name, phone) VALUES (%s, %s)", 
                                     (d['customer_name'], d['customer_phone']), commit=True)
            # Lấy ID khách vừa tạo
            cust_id_query = execute_query("SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1", fetch=True)
            cust_id = cust_id_query[0]['customer_id']

            # BƯỚC 2: Tạo đơn hàng với ID khách vừa tạo
            query = """INSERT INTO orders (order_id, customer_id, car_id, employee_id, order_date, order_value, status) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            execute_query(query, (d['order_id'], cust_id, d['car_id'], 
                                  d['employee_id'], date.today(), d['order_value'], d['status']), commit=True)
            self.load_orders()

    def edit_order(self, order):
        dlg = OrderDialog(self, order)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            query = """UPDATE orders SET car_id=%s, employee_id=%s, 
                       order_value=%s, status=%s WHERE order_id=%s"""
            execute_query(query, (d['car_id'], d['employee_id'], 
                                  d['order_value'], d['status'], d['order_id']), commit=True)
            self.load_orders()

    def delete_order(self, order):
        if QMessageBox.question(self, "Xác nhận", f"Xóa đơn {order['order_id']}?") == QMessageBox.StandardButton.Yes:
            execute_query("DELETE FROM orders WHERE order_id=%s", (order['order_id'],), commit=True)
            self.load_orders()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesManager()
    window.show()
    sys.exit(app.exec())