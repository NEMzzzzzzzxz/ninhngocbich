import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton, QLabel,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
                             QApplication, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from db_connection import execute_query


class EmployeeDialog(QDialog):
    def __init__(self, parent=None, emp=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin nhân viên")
        self.setFixedWidth(400)
        layout = QFormLayout(self)

        self.txt_id = QLineEdit()
        self.txt_name = QLineEdit()
        self.txt_position = QLineEdit("Nhân viên bán hàng")
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Đang làm", "Nghỉ phép", "Đã nghỉ"])

        if emp:
            self.txt_id.setText(emp['employee_id'])
            self.txt_name.setText(emp['full_name'])
            self.txt_position.setText(emp['position'])
            self.cb_status.setCurrentText(emp['status'])
        else:
            # Tự sinh mã nhân viên
            last = execute_query("SELECT employee_id FROM employees ORDER BY employee_id DESC LIMIT 1", fetch=True)
            if last and last[0]['employee_id']:
                num = int(last[0]['employee_id'][2:]) + 1
            else:
                num = 1
            self.txt_id.setText(f"NV{num:03d}")

        style = "padding:8px; border:1px solid #ddd; border-radius:5px;"
        for w in [self.txt_id, self.txt_name, self.txt_position, self.cb_status]:
            w.setStyleSheet(style)

        layout.addRow("Mã NV:", self.txt_id)
        layout.addRow("Họ tên:", self.txt_name)
        layout.addRow("Chức vụ:", self.txt_position)
        layout.addRow("Trạng thái:", self.cb_status)

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
            'employee_id': self.txt_id.text().strip(),
            'full_name': self.txt_name.text().strip(),
            'position': self.txt_position.text().strip(),
            'status': self.cb_status.currentText()
        }


class EmployeeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f8f9fa;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header = QHBoxLayout()
        title = QLabel("Quản lý nhân viên")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        btn_add = QPushButton("+ Thêm nhân viên")
        btn_add.clicked.connect(self.add_employee)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_add)
        layout.addLayout(header)

        # Thống kê
        self.stats_layout = QHBoxLayout()
        layout.addLayout(self.stats_layout)

        # Bảng nhân viên (có thêm cột Tài khoản)
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Mã NV", "Họ tên", "Chức vụ", "Xe đã bán",
            "Doanh thu (VNĐ)", "Hoa hồng (VNĐ)", "Trạng thái", "Tài khoản", "Thao tác"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.load_employees()

    def load_employees(self):
        """Lấy danh sách nhân viên và thông tin tài khoản (nếu có)"""
        query = """
            SELECT e.*, u.username 
            FROM employees e
            LEFT JOIN users u ON e.employee_id = u.employee_id
            ORDER BY e.employee_id
        """
        self.employees = execute_query(query, fetch=True)
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        for row, emp in enumerate(self.employees):
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(emp['employee_id']))
            self.table.setItem(row, 1, QTableWidgetItem(emp['full_name']))
            self.table.setItem(row, 2, QTableWidgetItem(emp['position']))
            self.table.setItem(row, 3, QTableWidgetItem(str(emp['cars_sold'] or 0)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{emp['revenue_total']:,.0f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{emp['commission_val']:,.0f}"))

            status_item = QTableWidgetItem(emp['status'])
            if emp['status'] == "Đang làm":
                status_item.setForeground(QColor("#28a745"))
            elif emp['status'] == "Nghỉ phép":
                status_item.setForeground(QColor("#f57c00"))
            else:
                status_item.setForeground(QColor("#dc3545"))
            self.table.setItem(row, 6, status_item)

            # Tài khoản
            username = emp['username'] if emp['username'] else ""
            user_item = QTableWidgetItem(username)
            if not username:
                user_item.setForeground(QColor("#aaa"))
                user_item.setText("Chưa có")
            self.table.setItem(row, 7, user_item)

            # Các nút chức năng
            container = QWidget()
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(0, 0, 0, 0)

            btn_edit = QPushButton("Sửa")
            btn_edit.setStyleSheet("color:#0061ff; border:none;")
            btn_edit.clicked.connect(lambda _, e=emp: self.edit_employee(e))

            btn_del = QPushButton("Xóa")
            btn_del.setStyleSheet("color:#dc3545; border:none;")
            btn_del.clicked.connect(lambda _, e=emp: self.delete_employee(e))

            # Nút tạo/đặt lại mật khẩu
            if emp['username']:
                btn_reset = QPushButton("Đặt lại MK")
                btn_reset.setStyleSheet("color:#ff9800; border:none;")
                btn_reset.clicked.connect(lambda _, e=emp: self.reset_password(e))
            else:
                btn_reset = QPushButton("Tạo TK")
                btn_reset.setStyleSheet("color:#4caf50; border:none;")
                btn_reset.clicked.connect(lambda _, e=emp: self.create_account(e))

            hbox.addWidget(btn_edit)
            hbox.addWidget(btn_del)
            hbox.addWidget(btn_reset)
            self.table.setCellWidget(row, 8, container)

        self.update_stats()

    def update_stats(self):
        for i in reversed(range(self.stats_layout.count())):
            w = self.stats_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        total = len(self.employees)
        active = sum(1 for e in self.employees if e['status'] == "Đang làm")
        total_cars = sum(e['cars_sold'] or 0 for e in self.employees)
        self.add_stat_card("Tổng nhân viên", str(total))
        self.add_stat_card("Đang làm", str(active))
        self.add_stat_card("Tổng xe bán", str(total_cars))

    def add_stat_card(self, title, value):
        card = QLabel(f"{title}\n{value}", alignment=Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet("background:white; border-radius:10px; padding:12px; font-weight:bold;")
        self.stats_layout.addWidget(card)

    # CRUD nhân viên
    def add_employee(self):
        dlg = EmployeeDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            exist = execute_query("SELECT employee_id FROM employees WHERE employee_id=%s", (data['employee_id'],), fetch=True)
            if exist:
                QMessageBox.warning(self, "Lỗi", f"Mã {data['employee_id']} đã tồn tại.")
                return
            query = """
                INSERT INTO employees (employee_id, full_name, position, cars_sold, revenue_total, commission_val, status)
                VALUES (%s, %s, %s, 0, 0, 0, %s)
            """
            execute_query(query, (data['employee_id'], data['full_name'], data['position'], data['status']), commit=True)
            self.load_employees()
            QMessageBox.information(self, "Thành công", "Đã thêm nhân viên. Bạn có thể tạo tài khoản đăng nhập cho nhân viên này.")
    
    def edit_employee(self, emp):
        dlg = EmployeeDialog(self, emp)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            query = "UPDATE employees SET full_name=%s, position=%s, status=%s WHERE employee_id=%s"
            execute_query(query, (data['full_name'], data['position'], data['status'], data['employee_id']), commit=True)
            self.load_employees()
            QMessageBox.information(self, "Thành công", "Đã cập nhật nhân viên.")
    
    def delete_employee(self, emp):
        # Kiểm tra đơn hàng
        orders = execute_query("SELECT COUNT(*) as cnt FROM orders WHERE employee_id=%s", (emp['employee_id'],), fetch=True)
        if orders and orders[0]['cnt'] > 0:
            QMessageBox.warning(self, "Không thể xóa", "Nhân viên đã có đơn hàng.")
            return
        # Xóa user trước (nếu có)
        execute_query("DELETE FROM users WHERE employee_id=%s", (emp['employee_id'],), commit=True)
        execute_query("DELETE FROM employees WHERE employee_id=%s", (emp['employee_id'],), commit=True)
        self.load_employees()
        QMessageBox.information(self, "Thành công", "Đã xóa nhân viên.")

    # Quản lý tài khoản đăng nhập
    def create_account(self, emp):
        username, ok = QInputDialog.getText(self, "Tạo tài khoản", "Nhập tên đăng nhập:")
        if not ok or not username.strip():
            return
        # Kiểm tra username đã tồn tại chưa
        exist = execute_query("SELECT username FROM users WHERE username=%s", (username.strip(),), fetch=True)
        if exist:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại.")
            return
        password, ok = QInputDialog.getText(self, "Đặt mật khẩu", "Nhập mật khẩu:", QLineEdit.EchoMode.Password)
        if not ok or not password:
            return
        # role có thể chọn: sales hoặc manager
        roles = ["sales", "manager"]
        role, ok = QInputDialog.getItem(self, "Phân quyền", "Chọn vai trò:", roles, 0, False)
        if not ok:
            return
        query = "INSERT INTO users (username, password, role, employee_id) VALUES (%s, %s, %s, %s)"
        execute_query(query, (username.strip(), password, role, emp['employee_id']), commit=True)
        self.load_employees()
        QMessageBox.information(self, "Thành công", f"Đã tạo tài khoản {username} cho nhân viên {emp['full_name']}.")
    
    def reset_password(self, emp):
        # Lấy username hiện tại
        user = execute_query("SELECT username FROM users WHERE employee_id=%s", (emp['employee_id'],), fetch=True)
        if not user:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy tài khoản.")
            return
        username = user[0]['username']
        new_pass, ok = QInputDialog.getText(self, "Đặt lại mật khẩu", f"Nhập mật khẩu mới cho {username}:", QLineEdit.EchoMode.Password)
        if ok and new_pass:
            execute_query("UPDATE users SET password=%s WHERE employee_id=%s", (new_pass, emp['employee_id']), commit=True)
            QMessageBox.information(self, "Thành công", "Đã đặt lại mật khẩu.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = EmployeeManager()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())