import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QPushButton, QStackedWidget, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import các trang
from Tongquan import DashboardPro
from Trangquanlykhoxe import InventoryManager
from Trangkhachhang import CustomerPage
from Trangquanlybanhang import SalesManager
from Tranglichhen import AppointmentPage
from Trangquanlynhanvien import EmployeeManager
from Trangbaocao import ReportPage
from Trangdichvu import ServiceManager

class MainApp(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role = role   # 'admin', 'manager', 'sales'
        self.setWindowTitle("Hệ thống Quản lý Auto Dealer Pro")
        self.resize(1280, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.setup_sidebar()

        # Khu vực nội dung
        self.stacked_pages = QStackedWidget()
        self.stacked_pages.addWidget(DashboardPro())      # 0
        self.stacked_pages.addWidget(InventoryManager())  # 1
        self.stacked_pages.addWidget(CustomerPage())      # 2
        self.stacked_pages.addWidget(SalesManager())      # 3
        self.stacked_pages.addWidget(AppointmentPage())   # 4
        self.stacked_pages.addWidget(EmployeeManager())   # 5
        self.stacked_pages.addWidget(ReportPage())        # 6
        self.stacked_pages.addWidget(ServiceManager())    # 7

        self.main_layout.addWidget(self.stacked_pages)

    def setup_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: white; border-right: 1px solid #ddd;")
        v_layout = QVBoxLayout(sidebar)
        
        title = QLabel("AutoPro")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3461ff; padding: 20px;")
        v_layout.addWidget(title)

        # Danh sách menu (text, index, required_role)
        all_menus = [
            ("📊 Tổng quan", 0, None),
            ("🚗 Kho xe", 1, None),
            ("👥 Khách hàng", 2, None),
            ("💰 Bán hàng", 3, None),
            ("📅 Lịch hẹn", 4, None),
            ("👷 Nhân viên", 5, "admin"),
            ("📈 Báo cáo", 6, "admin"),
            ("🔧 Dịch vụ", 7, None)
        ]

        self.btns = []
        for text, index, required_role in all_menus:
            if required_role is not None and self.role != required_role:
                continue
            btn = QPushButton(f"  {text}")
            btn.setFixedHeight(45)
            btn.setCheckable(True)
            btn.setStyleSheet(self.get_menu_style())
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            v_layout.addWidget(btn)
            self.btns.append(btn)

        v_layout.addStretch()
        self.btn_logout = QPushButton("  🚪 Đăng xuất")
        self.btn_logout.setFixedHeight(45)
        self.btn_logout.setStyleSheet(self.get_menu_style())
        v_layout.addWidget(self.btn_logout)
        
        self.main_layout.addWidget(sidebar)
        if self.btns:
            self.btns[0].setChecked(True)

    def get_menu_style(self):
        return """
            QPushButton { text-align: left; padding-left: 15px; border: none; border-radius: 8px; color: #555; }
            QPushButton:hover { background-color: #f0f4ff; color: #3461ff; }
            QPushButton:checked { background-color: #f0f4ff; color: #3461ff; font-weight: bold; }
        """

    def switch_page(self, index):
        self.stacked_pages.setCurrentIndex(index)
        for i, btn in enumerate(self.btns):
            btn.setChecked(i == index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainApp("admin")
    window.show()
    sys.exit(app.exec())