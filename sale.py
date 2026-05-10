import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFrame, QLabel, QPushButton, QStackedWidget, QApplication,
                             QSizePolicy, QMessageBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

# Import các trang
try:
    from Tongquan import DashboardPro
    from Trangquanlykhoxe import InventoryManager
    from Trangkhachhang import CustomerPage
    from Trangquanlybanhang import SalesManager
    from Tranglichhen import AppointmentPage
    from Trangdichvu import ServiceManager
except ImportError as e:
    print(f"Cảnh báo: Một số file giao diện chưa hoàn thiện: {e}")
    # Tạo stub nếu cần

class SalesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoPro Sales - Nhân viên")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
            #sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #ffffff, stop:1 #f8fafc);
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(4, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        sidebar.setGraphicsEffect(shadow)

        v = QVBoxLayout(sidebar)
        v.setContentsMargins(16, 24, 16, 24)
        v.setSpacing(15)

        logo_label = QLabel("🚗 AutoPro Sales")
        logo_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #1e3a5f; padding-bottom: 10px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(logo_label)

        menus = [
            ("📊 Tổng quan", 0), ("🚗 Kho xe", 1), ("👥 Khách hàng", 2),
            ("💰 Bán hàng", 3), ("📅 Lịch hẹn", 4), ("🔧 Dịch vụ", 5)
        ]
        self.btns = []
        for text, idx in menus:
            btn = QPushButton(f"  {text}")
            btn.setFixedHeight(45)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self.menu_btn_style())
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            v.addWidget(btn)
            self.btns.append(btn)

        v.addStretch()

        staff_frame = QFrame()
        staff_frame.setStyleSheet("background: #eef2ff; border-radius: 16px;")
        staff_layout = QHBoxLayout(staff_frame)
        avatar = QLabel("👤")
        avatar.setFixedSize(35, 35)
        avatar.setStyleSheet("background: #2c7da0; color: white; border-radius: 17px; font-size: 16px;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info = QVBoxLayout()
        name_label = QLabel("Nguyễn Văn A")
        name_label.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 12px;")
        role_label = QLabel("Nhân viên")
        role_label.setStyleSheet("font-size: 10px; color: #475569;")
        info.addWidget(name_label)
        info.addWidget(role_label)
        self.btn_logout = QPushButton("🚪")
        self.btn_logout.setFixedSize(35, 35)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setToolTip("Đăng xuất")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border-radius: 17px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #fee2e2;
                color: #ef4444;
            }
        """)
        self.btn_logout.clicked.connect(self.handle_logout)

        staff_layout.addWidget(avatar)
        staff_layout.addLayout(info)
        staff_layout.addWidget(self.btn_logout)
        v.addWidget(staff_frame)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: white; border-radius: 20px;")
        try:
            self.stack.addWidget(DashboardPro())
            self.stack.addWidget(InventoryManager())
            self.stack.addWidget(CustomerPage())
            self.stack.addWidget(SalesManager())
            self.stack.addWidget(AppointmentPage())
            self.stack.addWidget(ServiceManager())
        except:
            for i in range(6):
                self.stack.addWidget(QLabel(f"Trang {i} chưa được nạp..."))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, stretch=1)

        if self.btns:
            self.btns[0].setChecked(True)

    def menu_btn_style(self):
        return """
            QPushButton {
                text-align: left; padding-left: 15px; border: none;
                border-radius: 10px; color: #334155; font-weight: 500;
            }
            QPushButton:hover { background-color: #eef2ff; }
            QPushButton:checked { background-color: #2c7da0; color: white; }
        """

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.btns):
            btn.setChecked(i == idx)

    def handle_logout(self):
        confirm = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn đăng xuất và quay lại màn hình đăng nhập?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                from logiin import LoginPage
                self.login_win = LoginPage()
                self.login_win.show()
                self.close()
            except ImportError as e:
                QMessageBox.critical(self, "Lỗi", f"Không tìm thấy file 'logiin.py' hoặc Class 'LoginPage'.\nChi tiết: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SalesApp()
    window.show()
    sys.exit(app.exec())