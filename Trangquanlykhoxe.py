import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,
                             QMessageBox, QDialog, QFormLayout, QComboBox, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from db_connection import execute_query

class CarDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin xe")
        self.setFixedWidth(450)
        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Lấy danh sách thương hiệu
        brands = execute_query("SELECT brand_id, brand_name FROM brands ORDER BY brand_name", fetch=True)
        self.brand_map = {b['brand_name']: b['brand_id'] for b in brands}
        brand_names = list(self.brand_map.keys())

        self.txt_ma = QLineEdit()
        self.txt_ten = QLineEdit()
        self.cb_hang = QComboBox()
        self.cb_hang.addItems(brand_names)
        self.txt_gia = QLineEdit()
        self.txt_nam = QLineEdit()
        self.cb_trangthai = QComboBox()
        self.cb_trangthai.addItems(["Có sẵn", "Sắp về", "Đặt trước"])

        if data:
            self.txt_ma.setText(data['car_id'])
            self.txt_ten.setText(data['car_name'])
            self.cb_hang.setCurrentText(data['brand_name'])
            self.txt_gia.setText(str(data['price_val']))
            self.txt_nam.setText(str(data['production_year']))
            self.cb_trangthai.setCurrentText(data['status'])

        style = "padding: 8px; border: 1px solid #ddd; border-radius: 5px;"
        for w in [self.txt_ma, self.txt_ten, self.txt_gia, self.txt_nam, self.cb_hang, self.cb_trangthai]:
            w.setStyleSheet(style)

        layout.addRow("Mã xe:", self.txt_ma)
        layout.addRow("Tên xe:", self.txt_ten)
        layout.addRow("Hãng:", self.cb_hang)
        layout.addRow("Giá (VNĐ):", self.txt_gia)
        layout.addRow("Năm SX:", self.txt_nam)
        layout.addRow("Trạng thái:", self.cb_trangthai)

        btns = QHBoxLayout()
        btn_save = QPushButton("Lưu")
        btn_save.setStyleSheet("background:#0061ff; color:white; padding:8px; border-radius:5px;")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addRow(btns)

    def get_data(self):
        try:
            gia_str = self.txt_gia.text().replace(',', '').strip()
            gia = float(gia_str) if gia_str else 0.0
            nam = int(self.txt_nam.text().strip()) if self.txt_nam.text().strip() else 0
        except ValueError:
            gia = 0.0
            nam = 0
        return {
            'car_id': self.txt_ma.text().strip(),
            'car_name': self.txt_ten.text().strip(),
            'brand_name': self.cb_hang.currentText(),
            'price_val': gia,
            'production_year': nam,
            'status': self.cb_trangthai.currentText()
        }

class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f8f9fa;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,20,25,20)

        # Toolbar
        top = QHBoxLayout()
        btn_add = QPushButton("➕ Thêm xe")
        btn_add.clicked.connect(self.add_car)
        btn_add.setStyleSheet("padding:8px 16px; background:white; border-radius:8px;")
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Tìm theo tên hoặc hãng")
        self.search.setFixedWidth(300)
        self.search.textChanged.connect(self.filter_data)
        top.addWidget(btn_add)
        top.addStretch()
        top.addWidget(self.search)
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Mã xe","Tên xe","Hãng","Giá (VNĐ)","Năm SX","Trạng thái","Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        query = """
            SELECT c.car_id, c.car_name, b.brand_name, c.price_val,
                   c.production_year, c.status
            FROM cars c
            JOIN brands b ON c.brand = b.brand_id
            ORDER BY c.car_id
        """
        self.all_cars = execute_query(query, fetch=True) or []
        self.refresh_table(self.all_cars)

    def refresh_table(self, data_list):
        self.table.setRowCount(0)
        for row, car in enumerate(data_list):
            self.table.insertRow(row)
            self.table.setItem(row,0, QTableWidgetItem(car['car_id']))
            self.table.setItem(row,1, QTableWidgetItem(car['car_name']))
            self.table.setItem(row,2, QTableWidgetItem(car['brand_name']))
            self.table.setItem(row,3, QTableWidgetItem(f"{car['price_val']:,.0f}"))
            self.table.setItem(row,4, QTableWidgetItem(str(car['production_year'])))
            # Status color
            status = QTableWidgetItem(car['status'])
            color = "#28a745" if car['status']=="Có sẵn" else "#f57c00" if car['status']=="Sắp về" else "#0061ff"
            status.setForeground(QColor(color))
            self.table.setItem(row,5, status)
            # Buttons
            self.add_action_buttons(row, car['car_id'])
        self.table.resizeColumnsToContents()

    def add_action_buttons(self, row, car_id):
        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(0,0,0,0)
        btn_edit = QPushButton("Sửa")
        btn_edit.setStyleSheet("color:#0061ff; border:none;")
        btn_edit.clicked.connect(lambda: self.edit_car(car_id))
        btn_del = QPushButton("Xóa")
        btn_del.setStyleSheet("color:#dc3545; border:none;")
        btn_del.clicked.connect(lambda: self.delete_car(car_id))
        hbox.addWidget(btn_edit)
        hbox.addWidget(btn_del)
        self.table.setCellWidget(row,6, container)

    def add_car(self):
        dlg = CarDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            # Kiểm tra dữ liệu đầu vào
            if not data['car_id'] or not data['car_name']:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập mã xe và tên xe.")
                return
            if data['price_val'] <= 0:
                QMessageBox.warning(self, "Giá không hợp lệ", "Vui lòng nhập giá lớn hơn 0.")
                return
            if data['production_year'] < 1900 or data['production_year'] > 2100:
                QMessageBox.warning(self, "Năm sản xuất không hợp lệ", "Năm sản xuất phải từ 1900 đến 2100.")
                return

            # Lấy brand_id
            brand_id = execute_query("SELECT brand_id FROM brands WHERE brand_name=%s", (data['brand_name'],), fetch=True)
            if not brand_id:
                QMessageBox.warning(self,"Lỗi","Thương hiệu không tồn tại.")
                return
            brand_id = brand_id[0]['brand_id']
            query = """INSERT INTO cars (car_id, car_name, brand, price_val, production_year, status)
                       VALUES (%s,%s,%s,%s,%s,%s)"""
            result = execute_query(query, (data['car_id'], data['car_name'], brand_id,
                                           data['price_val'], data['production_year'], data['status']), commit=True)
            # result là lastrowid nếu thành công (có thể 0 nếu không có auto_increment), None nếu thất bại
            if result is not None:
                self.load_data()
                QMessageBox.information(self, "Thành công", f"Đã thêm xe {data['car_id']}.")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể thêm xe. Mã xe có thể bị trùng hoặc lỗi CSDL.")

    def edit_car(self, car_id):
        car = next((c for c in self.all_cars if c['car_id'] == car_id), None)
        if not car:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy xe.")
            return
        dlg = CarDialog(self, car)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            # Kiểm tra dữ liệu
            if not data['car_name']:
                QMessageBox.warning(self, "Thiếu thông tin", "Tên xe không được để trống.")
                return
            if data['price_val'] <= 0:
                QMessageBox.warning(self, "Giá không hợp lệ", "Vui lòng nhập giá lớn hơn 0.")
                return
            brand_id = execute_query("SELECT brand_id FROM brands WHERE brand_name=%s", (data['brand_name'],), fetch=True)
            if not brand_id:
                QMessageBox.warning(self,"Lỗi","Thương hiệu không tồn tại.")
                return
            brand_id = brand_id[0]['brand_id']
            query = """UPDATE cars SET car_name=%s, brand=%s, price_val=%s, production_year=%s, status=%s
                       WHERE car_id=%s"""
            result = execute_query(query, (data['car_name'], brand_id, data['price_val'],
                                           data['production_year'], data['status'], car_id), commit=True)
            if result is not False:  # execute_query trả về True nếu thành công (không fetch, commit)
                self.load_data()
                QMessageBox.information(self, "Thành công", f"Đã cập nhật xe {car_id}.")
            else:
                QMessageBox.critical(self, "Lỗi", "Cập nhật thất bại.")

    def delete_car(self, car_id):
        reply = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa xe {car_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = execute_query("DELETE FROM cars WHERE car_id=%s", (car_id,), commit=True)
            if result is not False:
                self.load_data()
                QMessageBox.information(self, "Thành công", f"Đã xóa xe {car_id}.")
            else:
                QMessageBox.critical(self, "Lỗi", "Xóa thất bại (có thể xe đã có đơn hàng liên quan).")

    def filter_data(self):
        keyword = self.search.text().lower().strip()
        if not keyword:
            self.refresh_table(self.all_cars)
        else:
            filtered = [c for c in self.all_cars 
                        if keyword in c['car_name'].lower() or keyword in c['brand_name'].lower()]
            self.refresh_table(filtered)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = InventoryManager()
    window.resize(1100, 600)
    window.show()
    sys.exit(app.exec())