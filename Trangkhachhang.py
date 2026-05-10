import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QGridLayout, QLabel, QLineEdit, QFrame, QDialog,
                             QFormLayout, QPushButton, QGraphicsDropShadowEffect, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from db_connection import execute_query


class CustomerDetailDialog(QDialog):
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Chi tiết: {customer['full_name']}")
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        avatar = QLabel(customer['full_name'][0].upper())
        avatar.setFixedSize(70, 70)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background:#0061ff; color:white; border-radius:35px; font-size:28px;")
        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        name = QLabel(customer['full_name'])
        name.setStyleSheet("font-size:20px; font-weight:bold;")
        layout.addWidget(name, alignment=Qt.AlignmentFlag.AlignCenter)

        info = QFrame()
        info.setStyleSheet("background:#f8faff; border-radius:10px; padding:10px;")
        form = QFormLayout(info)
        
        # Xử lý NULL an toàn
        phone = customer['phone'] or ''
        email = customer['email'] or ''
        address = customer['address'] or ''
        purchased = customer['total_purchased'] if customer['total_purchased'] is not None else 0
        spent = customer['total_spent'] if customer['total_spent'] is not None else 0.0
        
        form.addRow("📞 SĐT:", QLabel(phone))
        form.addRow("✉️ Email:", QLabel(email))
        form.addRow("📍 Địa chỉ:", QLabel(address))
        form.addRow("📦 Đã mua:", QLabel(str(purchased)))
        form.addRow("💰 Tổng chi:", QLabel(f"{spent:,.0f} VNĐ"))
        layout.addWidget(info)

        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)


class CustomerCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, customer):
        super().__init__()
        self.customer = customer
        self.setFixedSize(320, 240)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            CustomerCard { background:white; border-radius:12px; border:1px solid #eee; }
            CustomerCard:hover { border:1px solid #0061ff; background:#fcfdff; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        avatar = QLabel(customer['full_name'][0].upper())
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background:#e3f2fd; color:#1976d2; border-radius:20px;")
        top.addWidget(avatar)
        top.addStretch()
        top.addWidget(QLabel(f"#{customer['customer_id']}", styleSheet="color:#aaa;"))
        layout.addLayout(top)
        layout.addWidget(QLabel(customer['full_name'], styleSheet="font-size:16px; font-weight:bold;"))
        layout.addWidget(QLabel(f"📞 {customer['phone']}"))
        layout.addWidget(QLabel(f"✉️ {customer['email'] or ''}"))
        layout.addStretch()
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#eee;")
        layout.addWidget(line)
        stats = QHBoxLayout()
        
        # Xử lý NULL an toàn
        purchased = customer['total_purchased'] if customer['total_purchased'] is not None else 0
        spent = customer['total_spent'] if customer['total_spent'] is not None else 0.0
        
        stats.addWidget(QLabel(f"Mua: {purchased}", styleSheet="font-weight:bold;"))
        stats.addStretch()
        stats.addWidget(QLabel(f"{spent:,.0f}", styleSheet="color:#28a745; font-weight:bold;"))
        layout.addLayout(stats)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.customer)


class CustomerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f4f7fa;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo tên, SĐT hoặc email")
        self.search_input.textChanged.connect(self.filter_customers)
        layout.addWidget(self.search_input)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none; background:transparent;")
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.load_customers()

    def load_customers(self):
        query = "SELECT * FROM customers ORDER BY customer_id"
        self.customers = execute_query(query, fetch=True)
        # Đảm bảo các giá trị NULL được xử lý trước khi render
        for c in self.customers:
            if c['total_purchased'] is None:
                c['total_purchased'] = 0
            if c['total_spent'] is None:
                c['total_spent'] = 0.0
        self.render_cards(self.customers)

    def render_cards(self, data_list):
        # Xóa các widget cũ
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Thêm card mới
        for i, cust in enumerate(data_list):
            card = CustomerCard(cust)
            card.clicked.connect(self.show_detail)
            self.grid.addWidget(card, i // 3, i % 3)

    def filter_customers(self):
        txt = self.search_input.text().lower().strip()
        if not txt:
            self.render_cards(self.customers)
        else:
            filtered = [c for c in self.customers if txt in c['full_name'].lower() or
                        txt in c['phone'].lower() or
                        (c['email'] and txt in c['email'].lower())]
            self.render_cards(filtered)

    def show_detail(self, customer):
        dlg = CustomerDetailDialog(customer, self)
        dlg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = CustomerPage()
    window.resize(1100, 800)
    window.show()
    sys.exit(app.exec())