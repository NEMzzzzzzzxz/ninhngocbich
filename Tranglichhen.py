import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QFrame, QLabel, QPushButton, QDialog,
                             QFormLayout, QComboBox, QDateTimeEdit, QMessageBox,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor
from db_connection import execute_query


class AppointmentDialog(QDialog):
    def __init__(self, parent=None, appt=None):
        super().__init__(parent)
        self.setWindowTitle("Lịch hẹn")
        self.setFixedWidth(420)
        layout = QFormLayout(self)

        # Lấy danh sách khách hàng và xe
        customers = execute_query("SELECT customer_id, full_name, phone FROM customers", fetch=True)
        cars = execute_query("SELECT car_id, car_name FROM cars", fetch=True)

        self.cust_map = {f"{c['full_name']} - {c['phone']}": c['customer_id'] for c in customers}
        self.car_map = {c['car_name']: c['car_id'] for c in cars}

        self.cb_cust = QComboBox()
        self.cb_cust.addItems(self.cust_map.keys())
        self.cb_car = QComboBox()
        self.cb_car.addItems(self.car_map.keys())
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_edit.setCalendarPopup(True)
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Chờ xác nhận", "Đã xác nhận"])

        if appt:
            # Tìm đúng khách hàng và xe
            cust_name = next((k for k, v in self.cust_map.items() if v == appt['customer_id']), "")
            car_name = next((k for k, v in self.car_map.items() if v == appt['car_id']), "")
            self.cb_cust.setCurrentText(cust_name)
            self.cb_car.setCurrentText(car_name)

            # Ghép ngày và giờ (giờ có thể là timedelta, nên xử lý)
            if isinstance(appt['appt_time'], str):
                time_str = appt['appt_time']
            else:
                # Chuyển timedelta về string "HH:MM:SS"
                total_seconds = appt['appt_time'].total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            dt_str = f"{appt['appt_date']} {time_str}"
            dt = QDateTime.fromString(dt_str, "yyyy-MM-dd HH:mm:ss")
            if dt.isValid():
                self.dt_edit.setDateTime(dt)
            self.cb_status.setCurrentText(appt['status'])

        layout.addRow("Khách hàng:", self.cb_cust)
        layout.addRow("Xe:", self.cb_car)
        layout.addRow("Thời gian:", self.dt_edit)
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
        dt = self.dt_edit.dateTime()
        return {
            'customer_id': self.cust_map[self.cb_cust.currentText()],
            'car_id': self.car_map[self.cb_car.currentText()],
            'appt_date': dt.toString("yyyy-MM-dd"),
            'appt_time': dt.toString("HH:mm:ss"),
            'status': self.cb_status.currentText()
        }


class AppointmentItem(QFrame):
    def __init__(self, appt, on_edit, on_delete):
        super().__init__()
        self.setFixedHeight(90)
        self.setStyleSheet("background:white; border-radius:12px; border:1px solid #eee; margin-bottom:5px;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        # Xử lý timedelta an toàn
        if isinstance(appt['appt_time'], str):
            time_str = appt['appt_time']
        else:
            total_seconds = appt['appt_time'].total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            time_str = f"{hours:02d}:{minutes:02d}"

        time_label = QLabel(time_str)
        time_label.setStyleSheet("color:#0061ff; font-weight:bold;")
        layout.addWidget(time_label)

        info = QVBoxLayout()
        info.addWidget(QLabel(appt['customer_name'], styleSheet="font-weight:bold;"))
        info.addWidget(QLabel(f"📞 {appt['phone']}  🚗 {appt['car_name']}"))
        layout.addLayout(info, stretch=1)

        status_label = QLabel(appt['status'].upper())
        color = "#28a745" if appt['status'] == "Đã xác nhận" else "#f57c00"
        status_label.setStyleSheet(f"color:{color}; background:#e8f5e9; padding:6px 12px; border-radius:15px;")
        layout.addWidget(status_label)

        btn_edit = QPushButton("✎")
        btn_edit.clicked.connect(lambda: on_edit(appt))
        btn_del = QPushButton("✕")
        btn_del.clicked.connect(lambda: on_delete(appt))
        btn_edit.setStyleSheet("border:none; color:#0061ff;")
        btn_del.setStyleSheet("border:none; color:#dc3545;")
        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)


class AppointmentPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f4f7fa;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Left panel
        left = QVBoxLayout()
        header = QHBoxLayout()
        header.addWidget(QLabel("Lịch hẹn lái thử", styleSheet="font-size:28px; font-weight:800;"))
        btn_add = QPushButton("+ Tạo lịch")
        btn_add.clicked.connect(self.add_appointment)
        header.addStretch()
        header.addWidget(btn_add)
        left.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none; background:transparent;")
        self.container = QWidget()
        self.timeline = QVBoxLayout(self.container)
        self.timeline.setSpacing(10)
        self.scroll.setWidget(self.container)
        left.addWidget(self.scroll)

        # Right panel (stats)
        self.right = QFrame()
        self.right.setStyleSheet("background:white; border-radius:20px; padding:20px;")
        self.right_layout = QVBoxLayout(self.right)

        layout.addLayout(left, stretch=2)
        layout.addWidget(self.right, stretch=1)

        self.load_appointments()

    def load_appointments(self):
        # Lấy dữ liệu: chú ý TIME_FORMAT để tránh timedelta
        query = """
            SELECT 
                a.appointment_id,
                DATE_FORMAT(a.appt_date, '%Y-%m-%d') AS appt_date,
                TIME_FORMAT(a.appt_time, '%H:%i:%s') AS appt_time,
                a.status,
                c.customer_id,
                c.full_name AS customer_name,
                c.phone,
                car.car_id,
                car.car_name
            FROM appointments a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN cars car ON a.car_id = car.car_id
            ORDER BY a.appt_date, a.appt_time
        """
        self.appointments = execute_query(query, fetch=True)
        self.render_timeline()

    def render_timeline(self):
        # Xóa toàn bộ widget cũ
        for i in reversed(range(self.timeline.count())):
            w = self.timeline.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not self.appointments:
            self.timeline.addWidget(QLabel("Chưa có lịch hẹn nào.", alignment=Qt.AlignmentFlag.AlignCenter))
        else:
            grouped = {}
            for appt in self.appointments:
                grouped.setdefault(appt['appt_date'], []).append(appt)

            for date, apps in sorted(grouped.items()):
                date_label = QLabel(f"  {date}  ")
                date_label.setStyleSheet("color:#0061ff; font-weight:bold; background:#eef4ff; border-radius:5px; padding:5px;")
                self.timeline.addWidget(date_label)
                for a in apps:
                    self.timeline.addWidget(AppointmentItem(a, self.edit_appointment, self.delete_appointment))
        self.timeline.addStretch()
        self.update_stats()

    def update_stats(self):
        # Xóa thống kê cũ
        for i in reversed(range(self.right_layout.count())):
            w = self.right_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        total = len(self.appointments)
        confirmed = sum(1 for a in self.appointments if a['status'] == "Đã xác nhận")
        self.right_layout.addWidget(QLabel("TỔNG QUAN", styleSheet="font-weight:bold; font-size:14px; margin-bottom:10px;"))
        self.right_layout.addWidget(QLabel(f"📋 Tổng lịch hẹn: {total}"))
        self.right_layout.addWidget(QLabel(f"✅ Đã xác nhận: {confirmed}"))
        self.right_layout.addWidget(QLabel(f"⏳ Chờ xác nhận: {total - confirmed}"))
        self.right_layout.addStretch()

    def add_appointment(self):
        dlg = AppointmentDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            query = """INSERT INTO appointments (customer_id, car_id, appt_date, appt_time, status)
                       VALUES (%s, %s, %s, %s, %s)"""
            execute_query(query, (data['customer_id'], data['car_id'],
                                  data['appt_date'], data['appt_time'], data['status']), commit=True)
            self.load_appointments()

    def edit_appointment(self, appt):
        dlg = AppointmentDialog(self, appt)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            query = """UPDATE appointments SET customer_id=%s, car_id=%s, appt_date=%s, appt_time=%s, status=%s
                       WHERE appointment_id=%s"""
            execute_query(query, (data['customer_id'], data['car_id'],
                                  data['appt_date'], data['appt_time'], data['status'], appt['appointment_id']), commit=True)
            self.load_appointments()

    def delete_appointment(self, appt):
        reply = QMessageBox.question(self, "Xác nhận xóa",
                                     f"Bạn có chắc muốn xóa lịch hẹn của {appt['customer_name']}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            execute_query("DELETE FROM appointments WHERE appointment_id=%s", (appt['appointment_id'],), commit=True)
            self.load_appointments()


# ========== KIỂM TRA ĐỘC LẬP ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = AppointmentPage()
    window.resize(1100, 700)
    window.show()
    sys.exit(app.exec())