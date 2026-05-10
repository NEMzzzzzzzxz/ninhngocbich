import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton, QLabel,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
                             QDateEdit, QTabWidget, QFrame, QApplication)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from db_connection import execute_query

# ==================== DIALOG CHO DỊCH VỤ ====================
class ServiceDialog(QDialog):
    def __init__(self, parent=None, service=None):
        super().__init__(parent)
        self.setWindowTitle("Dịch vụ")
        self.setFixedWidth(400)
        layout = QFormLayout(self)

        self.txt_name = QLineEdit()
        self.txt_price = QLineEdit()
        if service:
            self.txt_name.setText(service['service_name'])
            self.txt_price.setText(str(service['price']))

        style = "padding:8px; border:1px solid #ddd; border-radius:5px;"
        self.txt_name.setStyleSheet(style)
        self.txt_price.setStyleSheet(style)

        layout.addRow("Tên dịch vụ:", self.txt_name)
        layout.addRow("Giá (VNĐ):", self.txt_price)

        btns = QHBoxLayout()
        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addRow(btns)

    def get_data(self):
        return {
            'service_name': self.txt_name.text(),
            'price': float(self.txt_price.text().replace(',', ''))
        }

# ==================== DIALOG CHO PHIẾU DỊCH VỤ (NHÂN VIÊN) ====================
class ServiceLogDialog(QDialog):
    def __init__(self, parent=None, log=None):
        super().__init__(parent)
        self.setWindowTitle("Phiếu dịch vụ")
        self.setFixedWidth(450)
        layout = QFormLayout(self)

        customers = execute_query("SELECT customer_id, full_name, phone FROM customers", fetch=True)
        cars = execute_query("SELECT car_id, car_name FROM cars", fetch=True)
        services = execute_query("SELECT service_id, service_name, price FROM services", fetch=True)

        self.cust_map = {f"{c['full_name']} - {c['phone']}": c['customer_id'] for c in customers}
        self.car_map = {c['car_name']: c['car_id'] for c in cars}
        self.serv_map = {s['service_name']: {'id': s['service_id'], 'price': float(s['price'])} for s in services}

        self.cb_cust = QComboBox()
        self.cb_cust.addItems(self.cust_map.keys())
        self.cb_car = QComboBox()
        self.cb_car.addItems(self.car_map.keys())
        self.cb_service = QComboBox()
        self.cb_service.addItems(self.serv_map.keys())
        self.cb_service.currentTextChanged.connect(self.update_price)

        self.txt_price = QLineEdit()
        self.txt_price.setReadOnly(True)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        if log:
            cust_name = next((k for k, v in self.cust_map.items() if v == log['customer_id']), "")
            car_name = next((k for k, v in self.car_map.items() if v == log['car_id']), "")
            serv_name = next((k for k, v in self.serv_map.items() if v['id'] == log['service_id']), "")
            self.cb_cust.setCurrentText(cust_name)
            self.cb_car.setCurrentText(car_name)
            self.cb_service.setCurrentText(serv_name)
            self.date_edit.setDate(QDate.fromString(str(log['log_date']), "yyyy-MM-dd"))
        else:
            self.update_price()

        style = "padding:8px; border:1px solid #ddd; border-radius:5px;"
        for w in [self.cb_cust, self.cb_car, self.cb_service, self.txt_price, self.date_edit]:
            w.setStyleSheet(style)

        layout.addRow("Khách hàng:", self.cb_cust)
        layout.addRow("Xe:", self.cb_car)
        layout.addRow("Dịch vụ:", self.cb_service)
        layout.addRow("Giá:", self.txt_price)
        layout.addRow("Ngày:", self.date_edit)

        btns = QHBoxLayout()
        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addRow(btns)

    def update_price(self):
        serv_name = self.cb_service.currentText()
        if serv_name in self.serv_map:
            self.txt_price.setText(f"{self.serv_map[serv_name]['price']:,.0f}")

    def get_data(self):
        serv_name = self.cb_service.currentText()
        return {
            'customer_id': self.cust_map[self.cb_cust.currentText()],
            'car_id': self.car_map[self.cb_car.currentText()],
            'service_id': self.serv_map[serv_name]['id'],
            'log_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'total_pay': self.serv_map[serv_name]['price']
        }

# ==================== TRANG QUẢN LÝ DỊCH VỤ CHÍNH ====================
class ServiceManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f8f9fa;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        self.tabs = QTabWidget()
        self.tab_services = QWidget()
        self.tab_logs = QWidget()
        self.tab_booking = QWidget()
        self.tabs.addTab(self.tab_services, "📋 Danh sách dịch vụ")
        self.tabs.addTab(self.tab_logs, "📜 Lịch sử sửa chữa")
        self.tabs.addTab(self.tab_booking, "📝 Đặt dịch vụ")
        layout.addWidget(self.tabs)

        # ---------- TAB DỊCH VỤ ----------
        sv_layout = QVBoxLayout(self.tab_services)
        header_sv = QHBoxLayout()
        title_sv = QLabel("Quản lý gói dịch vụ")
        title_sv.setStyleSheet("font-size:20px; font-weight:bold;")
        btn_add_service = QPushButton("+ Thêm dịch vụ")
        btn_add_service.clicked.connect(self.add_service)
        header_sv.addWidget(title_sv)
        header_sv.addStretch()
        header_sv.addWidget(btn_add_service)
        sv_layout.addLayout(header_sv)

        self.table_services = QTableWidget()
        self.table_services.setColumnCount(4)
        self.table_services.setHorizontalHeaderLabels(["ID", "Tên dịch vụ", "Giá (VNĐ)", "Thao tác"])
        self.table_services.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sv_layout.addWidget(self.table_services)

        # ---------- TAB LỊCH SỬ ----------
        log_layout = QVBoxLayout(self.tab_logs)
        header_log = QHBoxLayout()
        title_log = QLabel("Lịch sử sửa chữa")
        title_log.setStyleSheet("font-size:20px; font-weight:bold;")
        btn_add_log = QPushButton("+ Tạo phiếu dịch vụ")
        btn_add_log.clicked.connect(self.add_service_log)
        header_log.addWidget(title_log)
        header_log.addStretch()
        header_log.addWidget(btn_add_log)
        log_layout.addLayout(header_log)

        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background:white; border-radius:10px; padding:10px; margin-bottom:15px;")
        self.stats_layout = QHBoxLayout(self.stats_frame)
        log_layout.addWidget(self.stats_frame)

        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(7)
        self.table_logs.setHorizontalHeaderLabels(["ID", "Khách hàng", "Xe", "Dịch vụ", "Ngày", "Tổng tiền", "Thao tác"])
        self.table_logs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        log_layout.addWidget(self.table_logs)

        # ---------- TAB ĐẶT DỊCH VỤ ----------
        self.setup_booking_tab()

        # Load dữ liệu ban đầu
        self.load_services()
        self.load_service_logs()

    # ==================== TAB DỊCH VỤ ====================
    def load_services(self):
        query = "SELECT service_id, service_name, price FROM services ORDER BY service_id"
        self.services = execute_query(query, fetch=True)
        self.refresh_services_table()

    def refresh_services_table(self):
        self.table_services.setRowCount(0)
        for row, sv in enumerate(self.services):
            self.table_services.insertRow(row)
            self.table_services.setItem(row, 0, QTableWidgetItem(str(sv['service_id'])))
            self.table_services.setItem(row, 1, QTableWidgetItem(sv['service_name']))
            self.table_services.setItem(row, 2, QTableWidgetItem(f"{sv['price']:,.0f}"))

            btn_edit = QPushButton("Sửa")
            btn_edit.setStyleSheet("color:#0061ff; border:none;")
            btn_edit.clicked.connect(lambda _, s=sv: self.edit_service(s))
            btn_del = QPushButton("Xóa")
            btn_del.setStyleSheet("color:#dc3545; border:none;")
            btn_del.clicked.connect(lambda _, s=sv: self.delete_service(s))
            container = QWidget()
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(0,0,0,0)
            hbox.addWidget(btn_edit)
            hbox.addWidget(btn_del)
            self.table_services.setCellWidget(row, 3, container)

    def add_service(self):
        dlg = ServiceDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            query = "INSERT INTO services (service_name, price) VALUES (%s, %s)"
            execute_query(query, (data['service_name'], data['price']), commit=True)
            self.load_services()

    def edit_service(self, service):
        dlg = ServiceDialog(self, service)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            query = "UPDATE services SET service_name=%s, price=%s WHERE service_id=%s"
            execute_query(query, (data['service_name'], data['price'], service['service_id']), commit=True)
            self.load_services()

    def delete_service(self, service):
        check = execute_query("SELECT COUNT(*) as cnt FROM service_logs WHERE service_id=%s", (service['service_id'],), fetch=True)
        if check and check[0]['cnt'] > 0:
            QMessageBox.warning(self, "Không thể xóa", "Dịch vụ đã có trong lịch sử sửa chữa!")
            return
        if QMessageBox.question(self, "Xác nhận", f"Xóa dịch vụ {service['service_name']}?") == QMessageBox.StandardButton.Yes:
            execute_query("DELETE FROM services WHERE service_id=%s", (service['service_id'],), commit=True)
            self.load_services()

    # ==================== TAB LỊCH SỬ ====================
    def load_service_logs(self):
        query = """
            SELECT sl.log_id, c.full_name AS customer_name, sl.car_name, s.service_name,
                   sl.log_date, sl.total_pay, sl.customer_id, sl.service_id
            FROM service_logs sl
            JOIN customers c ON sl.customer_id = c.customer_id
            JOIN services s ON sl.service_id = s.service_id
            ORDER BY sl.log_date DESC
        """
        self.logs = execute_query(query, fetch=True)
        self.refresh_logs_table()
        self.update_stats()

    def refresh_logs_table(self):
        self.table_logs.setRowCount(0)
        for row, log in enumerate(self.logs):
            self.table_logs.insertRow(row)
            self.table_logs.setItem(row, 0, QTableWidgetItem(str(log['log_id'])))
            self.table_logs.setItem(row, 1, QTableWidgetItem(log['customer_name']))
            self.table_logs.setItem(row, 2, QTableWidgetItem(log['car_name']))
            self.table_logs.setItem(row, 3, QTableWidgetItem(log['service_name']))
            self.table_logs.setItem(row, 4, QTableWidgetItem(str(log['log_date'])))
            self.table_logs.setItem(row, 5, QTableWidgetItem(f"{log['total_pay']:,.0f}"))

            btn_edit = QPushButton("Sửa")
            btn_edit.setStyleSheet("color:#0061ff; border:none;")
            btn_edit.clicked.connect(lambda _, l=log: self.edit_service_log(l))
            btn_del = QPushButton("Xóa")
            btn_del.setStyleSheet("color:#dc3545; border:none;")
            btn_del.clicked.connect(lambda _, l=log: self.delete_service_log(l))
            container = QWidget()
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(0,0,0,0)
            hbox.addWidget(btn_edit)
            hbox.addWidget(btn_del)
            self.table_logs.setCellWidget(row, 6, container)

    def update_stats(self):
        for i in reversed(range(self.stats_layout.count())):
            w = self.stats_layout.itemAt(i).widget()
            if w: w.deleteLater()
        total_revenue = sum(log['total_pay'] for log in self.logs)
        total_count = len(self.logs)
        self.add_stat_card("📊 Tổng số phiếu", str(total_count))
        self.add_stat_card("💰 Tổng doanh thu", f"{total_revenue:,.0f} VNĐ")

    def add_stat_card(self, title, value):
        card = QLabel(f"{title}\n{value}", alignment=Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet("background:white; border-radius:10px; padding:12px; font-weight:bold; border:1px solid #ddd;")
        self.stats_layout.addWidget(card)

    def add_service_log(self):
        dlg = ServiceLogDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            car = execute_query("SELECT car_name FROM cars WHERE car_id=%s", (data['car_id'],), fetch=True)
            car_name = car[0]['car_name'] if car else ""
            query = "INSERT INTO service_logs (customer_id, car_name, service_id, log_date, total_pay) VALUES (%s,%s,%s,%s,%s)"
            execute_query(query, (data['customer_id'], car_name, data['service_id'], data['log_date'], data['total_pay']), commit=True)
            self.load_service_logs()

    def edit_service_log(self, log):
        car_res = execute_query("SELECT car_id FROM cars WHERE car_name=%s", (log['car_name'],), fetch=True)
        car_id = car_res[0]['car_id'] if car_res else None
        log_data = {
            'customer_id': log['customer_id'],
            'car_id': car_id,
            'service_id': log['service_id'],
            'log_date': log['log_date'],
            'total_pay': log['total_pay']
        }
        dlg = ServiceLogDialog(self, log_data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            car = execute_query("SELECT car_name FROM cars WHERE car_id=%s", (data['car_id'],), fetch=True)
            car_name = car[0]['car_name'] if car else ""
            query = "UPDATE service_logs SET customer_id=%s, car_name=%s, service_id=%s, log_date=%s, total_pay=%s WHERE log_id=%s"
            execute_query(query, (data['customer_id'], car_name, data['service_id'], data['log_date'], data['total_pay'], log['log_id']), commit=True)
            self.load_service_logs()

    def delete_service_log(self, log):
        if QMessageBox.question(self, "Xác nhận", f"Xóa phiếu dịch vụ ID {log['log_id']}?") == QMessageBox.StandardButton.Yes:
            execute_query("DELETE FROM service_logs WHERE log_id=%s", (log['log_id'],), commit=True)
            self.load_service_logs()

    # ==================== TAB ĐẶT DỊCH VỤ (Chọn xe từ combobox) ====================
    def setup_booking_tab(self):
        layout = QVBoxLayout(self.tab_booking)
        layout.setSpacing(15)

        form_widget = QFrame()
        form_widget.setStyleSheet("background:white; border-radius:10px; padding:20px;")
        form_layout = QFormLayout(form_widget)

        self.booking_cust_name = QLineEdit()
        self.booking_cust_phone = QLineEdit()
        self.booking_cust_email = QLineEdit()
        self.booking_cust_address = QLineEdit()

        # Load danh sách xe từ database
        cars = execute_query("SELECT car_id, car_name FROM cars", fetch=True)
        self.car_map = {c['car_name']: c['car_id'] for c in cars}
        self.booking_cb_car = QComboBox()
        self.booking_cb_car.addItems(self.car_map.keys())

        # Load danh sách dịch vụ
        services = execute_query("SELECT service_id, service_name, price FROM services", fetch=True)
        self.booking_service_map = {s['service_name']: {'id': s['service_id'], 'price': float(s['price'])} for s in services}
        self.booking_cb_service = QComboBox()
        self.booking_cb_service.addItems(self.booking_service_map.keys())
        self.booking_cb_service.currentTextChanged.connect(self.update_booking_price)

        self.booking_txt_price = QLineEdit()
        self.booking_txt_price.setReadOnly(True)

        self.booking_date = QDateEdit()
        self.booking_date.setDate(QDate.currentDate())
        self.booking_date.setCalendarPopup(True)

        style = "padding:8px; border:1px solid #ddd; border-radius:5px;"
        for w in [self.booking_cust_name, self.booking_cust_phone, self.booking_cust_email,
                  self.booking_cust_address, self.booking_cb_car, self.booking_cb_service,
                  self.booking_txt_price, self.booking_date]:
            w.setStyleSheet(style)

        form_layout.addRow("Họ tên khách:", self.booking_cust_name)
        form_layout.addRow("Số điện thoại:", self.booking_cust_phone)
        form_layout.addRow("Email:", self.booking_cust_email)
        form_layout.addRow("Địa chỉ:", self.booking_cust_address)
        form_layout.addRow("Chọn xe:", self.booking_cb_car)          # Combobox chọn xe
        form_layout.addRow("Dịch vụ:", self.booking_cb_service)
        form_layout.addRow("Giá:", self.booking_txt_price)
        form_layout.addRow("Ngày đặt:", self.booking_date)

        btn_submit = QPushButton("Đặt dịch vụ")
        btn_submit.setStyleSheet("background:#0061ff; color:white; padding:12px; font-weight:bold; border-radius:8px;")
        btn_submit.clicked.connect(self.submit_booking)

        layout.addWidget(form_widget)
        layout.addWidget(btn_submit)
        layout.addStretch()

        self.update_booking_price()

    def update_booking_price(self):
        serv_name = self.booking_cb_service.currentText()
        if serv_name in self.booking_service_map:
            self.booking_txt_price.setText(f"{self.booking_service_map[serv_name]['price']:,.0f}")

    def submit_booking(self):
        name = self.booking_cust_name.text().strip()
        phone = self.booking_cust_phone.text().strip()
        car_name = self.booking_cb_car.currentText().strip()   # Lấy tên xe từ combobox
        if not name or not phone:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ họ tên và số điện thoại.")
            return

        # Kiểm tra khách hàng theo số điện thoại
        existing = execute_query("SELECT customer_id FROM customers WHERE phone=%s", (phone,), fetch=True)
        if existing:
            customer_id = existing[0]['customer_id']
            # Cập nhật thông tin khách hàng nếu có thay đổi
            if name:
                execute_query("UPDATE customers SET full_name=%s WHERE customer_id=%s", (name, customer_id), commit=True)
            if self.booking_cust_email.text():
                execute_query("UPDATE customers SET email=%s WHERE customer_id=%s", (self.booking_cust_email.text(), customer_id), commit=True)
            if self.booking_cust_address.text():
                execute_query("UPDATE customers SET address=%s WHERE customer_id=%s", (self.booking_cust_address.text(), customer_id), commit=True)
        else:
            # Tạo khách hàng mới
            query = "INSERT INTO customers (full_name, phone, email, address, total_purchased, total_spent) VALUES (%s,%s,%s,%s,0,0)"
            execute_query(query, (name, phone, self.booking_cust_email.text(), self.booking_cust_address.text()), commit=True)
            new_cust = execute_query("SELECT customer_id FROM customers WHERE phone=%s", (phone,), fetch=True)
            customer_id = new_cust[0]['customer_id'] if new_cust else None

        if not customer_id:
            QMessageBox.critical(self, "Lỗi", "Không thể xác định hoặc tạo khách hàng.")
            return

        # Lấy thông tin dịch vụ
        serv_name = self.booking_cb_service.currentText()
        service_id = self.booking_service_map[serv_name]['id']
        total_pay = self.booking_service_map[serv_name]['price']
        log_date = self.booking_date.date().toString("yyyy-MM-dd")

        # Ghi phiếu dịch vụ
        query = "INSERT INTO service_logs (customer_id, car_name, service_id, log_date, total_pay) VALUES (%s,%s,%s,%s,%s)"
        execute_query(query, (customer_id, car_name, service_id, log_date, total_pay), commit=True)

        QMessageBox.information(self, "Thành công", f"Đã đặt dịch vụ {serv_name} thành công!\nTổng tiền: {total_pay:,.0f} VNĐ")

        # Xóa form
        self.booking_cust_name.clear()
        self.booking_cust_phone.clear()
        self.booking_cust_email.clear()
        self.booking_cust_address.clear()
        self.booking_cb_car.setCurrentIndex(0)
        self.booking_cb_service.setCurrentIndex(0)
        self.booking_date.setDate(QDate.currentDate())

        # Refresh tab lịch sử và thống kê
        self.load_service_logs()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = ServiceManager()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())