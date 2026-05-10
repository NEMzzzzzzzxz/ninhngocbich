import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from db_connection import execute_query

class ReportPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f8f9fa;")
        main = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25,20,25,20)

        layout.addWidget(QLabel("Báo cáo phân tích", styleSheet="font-size:24px; font-weight:bold;"))

        # Doanh thu theo hãng
        brand_rev = execute_query("""
            SELECT b.brand_name, COALESCE(SUM(o.order_value),0) as revenue
            FROM brands b
            LEFT JOIN cars c ON b.brand_id = c.brand
            LEFT JOIN orders o ON c.car_id = o.car_id AND o.status='Hoàn thành'
            GROUP BY b.brand_id
        """, fetch=True)
        brands = [b['brand_name'] for b in brand_rev]
        # Chuyển Decimal sang float
        revenues = [float(b['revenue'])/1e6 for b in brand_rev]

        bar = pg.PlotWidget()
        bar.setBackground('w')
        bar.setTitle("Doanh thu theo hãng (triệu VNĐ)")
        x = list(range(len(brands)))
        bg = pg.BarGraphItem(x=x, height=revenues, width=0.6, brush='#3461ff')
        bar.addItem(bg)
        bar.getAxis('bottom').setTicks([[(i, brands[i]) for i in x]])
        layout.addWidget(bar)

        # Top nhân viên bán chạy
        top_emp = execute_query("""
            SELECT full_name, cars_sold FROM employees ORDER BY cars_sold DESC LIMIT 5
        """, fetch=True)
        emp_names = [e['full_name'] for e in top_emp]
        emp_sales = [e['cars_sold'] for e in top_emp]  # cars_sold đã là int

        line = pg.PlotWidget()
        line.setBackground('w')
        line.setTitle("Top 5 nhân viên bán nhiều xe nhất")
        x_emp = list(range(len(emp_names)))
        line.plot(x_emp, emp_sales, pen=pg.mkPen(color='#ff7f0e', width=3), symbol='o', symbolBrush='#ff7f0e')
        line.getAxis('bottom').setTicks([[(i, name) for i, name in enumerate(emp_names)]])
        layout.addWidget(line)

        scroll.setWidget(content)
        main.addWidget(scroll)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = ReportPage()
    window.resize(1100, 800)
    window.show()
    sys.exit(app.exec())