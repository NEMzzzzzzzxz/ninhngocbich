import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from logiin import LoginPage
from Trangchinh import MainApp as AdminApp
from sale import SalesApp

class AppController:
    def __init__(self):
        self.login_window = LoginPage()
        self.main_window = None
        self.login_window.login_confirmed.connect(self.show_main)
        self.login_window.show()

    def show_main(self, role):
        if role == 'admin':
            self.main_window = AdminApp(role)   # ✅ Đã sửa: thêm role
        else:   # 'sales', 'manager'
            self.main_window = SalesApp()

        # Kết nối nút logout nếu có
        if hasattr(self.main_window, 'btn_logout'):
            self.main_window.btn_logout.clicked.connect(self.logout)
        self.main_window.show()
        self.login_window.close()

    def logout(self):
        self.main_window.close()
        # Tạo lại login window mới
        self.login_window = LoginPage()
        self.login_window.login_confirmed.connect(self.show_main)
        self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    controller = AppController()
    sys.exit(app.exec())