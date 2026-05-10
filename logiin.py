import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from db_connection import execute_query

class LoginPage(QWidget):
    # Tín hiệu thông báo đăng nhập thành công, kèm theo role
    login_confirmed = pyqtSignal(str)  # sẽ truyền role

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập - Auto Dealer Pro")
        self.setFixedSize(1100, 700)
        self.setStyleSheet("background-color: #f0f2f5;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Banner bên trái
        self.left_frame = QFrame()
        self.left_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0061ff, stop:1 #60efff);")
        left_layout = QVBoxLayout(self.left_frame)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QLabel("AutoPro")
        logo.setStyleSheet("color: white; font-size: 48px; font-weight: 800;")
        left_layout.addWidget(logo)
        main_layout.addWidget(self.left_frame, stretch=1)

        # Form bên phải
        self.right_frame = QFrame()
        self.right_frame.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(self.right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_container = QFrame()
        form_container.setFixedWidth(380)
        form_v = QVBoxLayout(form_container)
        
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Tên đăng nhập")
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Mật khẩu")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)

        style = "padding: 15px; border: 1px solid #ddd; border-radius: 10px; background: #f9f9f9;"
        self.txt_user.setStyleSheet(style)
        self.txt_pass.setStyleSheet(style)

        self.btn_login = QPushButton("ĐĂNG NHẬP")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("background: #0061ff; color: white; padding: 15px; border-radius: 10px; font-weight: bold;")
        self.btn_login.clicked.connect(self.handle_login)

        form_v.addWidget(QLabel("Chào mừng trở lại!", styleSheet="font-size: 24px; font-weight: bold;"))
        form_v.addSpacing(20)
        form_v.addWidget(self.txt_user)
        form_v.addWidget(self.txt_pass)
        form_v.addWidget(self.btn_login)

        right_layout.addWidget(form_container)
        main_layout.addWidget(self.right_frame, stretch=1)

    def handle_login(self):
        username = self.txt_user.text().strip()
        password = self.txt_pass.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu.")
            return
        
        # Truy vấn kiểm tra tài khoản trong bảng users, lấy role
        query = "SELECT username, role FROM users WHERE username=%s AND password=%s"
        result = execute_query(query, (username, password), fetch=True)
        if result:
            role = result[0]['role']
            self.login_confirmed.emit(role)   # gửi role đi
        else:
            QMessageBox.warning(self, "Thất bại", "Sai tên đăng nhập hoặc mật khẩu!")