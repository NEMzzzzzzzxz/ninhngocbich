import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from db_connection import execute_query

class DashboardPro(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f8f9fa;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,20,25,20)

        header = QLabel("Tổng quan hệ thống")
        header.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(header)

        # Stats cards
        stats = QHBoxLayout()
        self.add_stat_card(stats, "Tổng xe trong kho", self.get_total_cars(), "#3461ff")
        self.add_stat_card(stats, "Khách hàng", self.get_total_customers(), "#28a745")
        self.add_stat_card(stats, "Doanh thu tháng này", self.get_monthly_revenue(), "#6f42c1")
        self.add_stat_card(stats, "Xe đã bán (tháng)", self.get_cars_sold_month(), "#fd7e14")
        layout.addLayout(stats)

        # Chart
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background:white; border-radius:12px; padding:10px;")
        chart_v = QVBoxLayout(chart_frame)
        chart_v.addWidget(QLabel("Biến động doanh thu 6 tháng (triệu VNĐ)"))
        self.plot = pg.PlotWidget()
        self.plot.setBackground('w')
        self.plot.showGrid(x=True, y=True)
        chart_v.addWidget(self.plot)
        layout.addWidget(chart_frame)
        self.load_chart_data()

    def add_stat_card(self, layout, title, value, color):
        card = QFrame()
        card.setStyleSheet("background:white; border-radius:12px; padding:15px;")
        v = QVBoxLayout(card)
        v.addWidget(QLabel(title, styleSheet="color:#777;"))
        v.addWidget(QLabel(str(value), styleSheet=f"font-size:24px; font-weight:bold; color:{color};"))
        layout.addWidget(card)

    def get_total_cars(self):
        result = execute_query("SELECT COUNT(*) as total FROM cars", fetch=True)
        return result[0]['total'] if result else 0

    def get_total_customers(self):
        result = execute_query("SELECT COUNT(*) as total FROM customers", fetch=True)
        return result[0]['total']

    def get_monthly_revenue(self):
        result = execute_query("""
            SELECT COALESCE(SUM(order_value),0) as revenue FROM orders
            WHERE MONTH(order_date)=MONTH(CURDATE()) AND YEAR(order_date)=YEAR(CURDATE()) AND status='Hoàn thành'
        """, fetch=True)
        revenue = float(result[0]['revenue']) if result and result[0]['revenue'] else 0.0
        return f"{revenue/1e6:,.0f} tr"

    def get_cars_sold_month(self):
        result = execute_query("""
            SELECT COUNT(*) as sold FROM orders
            WHERE MONTH(order_date)=MONTH(CURDATE()) AND YEAR(order_date)=YEAR(CURDATE()) AND status='Hoàn thành'
        """, fetch=True)
        return result[0]['sold'] if result else 0

    def load_chart_data(self):
        query = """
            SELECT DATE_FORMAT(order_date, '%Y-%m') as month, SUM(order_value) as total
            FROM orders
            WHERE status='Hoàn thành' AND order_date >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH)
            GROUP BY month ORDER BY month
        """
        data = execute_query(query, fetch=True)
        if data:
            months = [d['month'] for d in data]
            revenues = [float(d['total'])/1e6 for d in data]
            x = list(range(len(months)))  # tạo các giá trị số cho trục X
            self.plot.plot(x, revenues, pen=pg.mkPen(color='#6f42c1', width=3), symbol='o')
            # Gán nhãn tháng lên trục X
            ticks = [[(i, m) for i, m in enumerate(months)]]
            self.plot.getAxis('bottom').setTicks(ticks)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = DashboardPro()
    window.resize(1100, 700)
    window.show()
    sys.exit(app.exec())