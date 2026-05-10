-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th5 10, 2026 lúc 08:08 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `auto_dealer_pro`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `appointments`
--

CREATE TABLE `appointments` (
  `appointment_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `car_id` varchar(20) DEFAULT NULL,
  `appt_date` date NOT NULL,
  `appt_time` time NOT NULL,
  `status` enum('Đã xác nhận','Chờ xác nhận') DEFAULT 'Chờ xác nhận'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `appointments`
--

INSERT INTO `appointments` (`appointment_id`, `customer_id`, `car_id`, `appt_date`, `appt_time`, `status`) VALUES
(1, 1, 'C001', '2026-05-10', '09:00:00', 'Chờ xác nhận'),
(2, 1, 'C005', '2026-05-08', '01:18:26', 'Chờ xác nhận');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `brands`
--

CREATE TABLE `brands` (
  `brand_id` int(11) NOT NULL,
  `brand_name` varchar(50) NOT NULL,
  `country` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `brands`
--

INSERT INTO `brands` (`brand_id`, `brand_name`, `country`) VALUES
(1, 'Toyota', 'Nhật Bản'),
(2, 'Ford', 'Mỹ'),
(3, 'Mercedes', 'Đức'),
(4, 'Honda', 'Nhật Bản'),
(5, 'BMW', 'Đức'),
(6, 'Mazda', 'Nhật Bản'),
(7, 'Hyundai', 'Hàn Quốc');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `cars`
--

CREATE TABLE `cars` (
  `car_id` varchar(20) NOT NULL,
  `car_name` varchar(100) NOT NULL,
  `brand` int(11) DEFAULT NULL,
  `price_val` decimal(15,2) NOT NULL,
  `production_year` int(4) DEFAULT 2024,
  `status` enum('Có sẵn','Sắp về','Đặt trước') DEFAULT 'Có sẵn'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `cars`
--

INSERT INTO `cars` (`car_id`, `car_name`, `brand`, `price_val`, `production_year`, `status`) VALUES
('C001', 'Toyota Camry', 1, 1050000000.00, 2024, 'Có sẵn'),
('C002', 'Toyota Corolla', 1, 750000000.00, 2024, 'Có sẵn'),
('C003', 'Ford Ranger', 2, 950000000.00, 2025, 'Có sẵn'),
('C004', 'Ford Everest', 2, 1350000000.00, 2024, 'Đặt trước'),
('C005', 'Mercedes C300', 3, 2100000000.00, 2025, 'Có sẵn'),
('C006', 'Mercedes E450', 3, 3200000000.00, 2025, 'Sắp về'),
('C007', 'Honda CR-V', 4, 1100000000.00, 2024, 'Có sẵn'),
('C008', 'Honda Civic', 6, 850000000.00, 2024, 'Đặt trước'),
('C009', 'BMW 320i', 5, 1900000000.00, 2025, 'Có sẵn'),
('C010', 'Mazda CX-5', 6, 890000000.00, 2024, 'Có sẵn'),
('C11', 'SA', 5, 222.00, 2033, 'Có sẵn'),
('C12', 'ABC', 5, 222222.00, 2028, 'Có sẵn');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `total_purchased` int(11) DEFAULT 0,
  `total_spent` decimal(18,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `customers`
--

INSERT INTO `customers` (`customer_id`, `full_name`, `phone`, `email`, `address`, `total_purchased`, `total_spent`) VALUES
(1, 'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com', 'Số 1 Lê Lợi, Hà Nội', 3, 5333333333.00),
(2, 'Trần Thị Bình', '0912345678', 'binh.tran@email.com', 'Số 2 Nguyễn Huệ, TP.HCM', 1, 1200000000.00),
(3, 'Lê Hoàng Cường', '0923456789', 'cuong.le@email.com', 'Số 3 Trần Phú, Đà Nẵng', 0, 0.00),
(4, 'Phạm Thị Dung', '0934567890', 'dung.pham@email.com', 'Số 4 Hùng Vương, Hải Phòng', 1, 950000000.00),
(5, 'Hoàng Văn Em', '0945678901', 'em.hoang@email.com', 'Số 5 Nguyễn Trãi, Cần Thơ', 0, 0.00),
(6, 'sà', '43634', 'ds', 'dssg', 0, 500000.00),
(7, 'Trân', '0020202', 'a@gmail.com', NULL, 0, NULL),
(8, 'úgabig', '0303030', NULL, NULL, 0, 0.00),
(9, 'jfjd', '303003', NULL, NULL, 0, 0.00),
(10, 'êu', '222', NULL, NULL, 0, 0.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `employees`
--

CREATE TABLE `employees` (
  `employee_id` varchar(20) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `position` varchar(50) DEFAULT 'Nhân viên bán hàng',
  `cars_sold` int(11) DEFAULT 0,
  `revenue_total` decimal(18,2) DEFAULT 0.00,
  `commission_val` decimal(15,2) DEFAULT 0.00,
  `status` enum('Đang làm','Nghỉ phép','Đã nghỉ') DEFAULT 'Đang làm'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `employees`
--

INSERT INTO `employees` (`employee_id`, `full_name`, `position`, `cars_sold`, `revenue_total`, `commission_val`, `status`) VALUES
('NV001', 'Nguyễn Văn D', 'Trưởng phòng', 3, 5273333333.00, 26366666.67, 'Nghỉ phép'),
('NV002', 'Trần Văn B', 'Nhân viên', 45, 54500000000.00, 272500000.00, 'Đang làm'),
('NV003', 'Phạm Thị C', 'Nhân viên', 28, 35000000000.00, 175000000.00, 'Đang làm'),
('NV004', 'Lê Thị E', 'Nhân viên', 15, 18900000000.00, 94500000.00, 'Nghỉ phép'),
('NV005', 'tttt', 'Nhân viên bán hàng', 0, 0.00, 0.00, 'Đang làm');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `orders`
--

CREATE TABLE `orders` (
  `order_id` varchar(20) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `car_id` varchar(20) DEFAULT NULL,
  `employee_id` varchar(20) DEFAULT NULL,
  `order_date` date NOT NULL,
  `order_value` decimal(15,2) NOT NULL,
  `status` enum('Hoàn thành','Đang xử lý','Chờ xử lý') DEFAULT 'Chờ xử lý'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `orders`
--

INSERT INTO `orders` (`order_id`, `customer_id`, `car_id`, `employee_id`, `order_date`, `order_value`, `status`) VALUES
('HD001', 1, 'C001', 'NV001', '2026-04-20', 1050000000.00, 'Hoàn thành'),
('HD002', 2, 'C007', 'NV002', '2026-04-22', 1100000000.00, 'Hoàn thành'),
('HD003', 1, 'C003', 'NV003', '2026-04-25', 950000000.00, 'Hoàn thành'),
('HD004', 4, 'C010', 'NV001', '2026-04-28', 890000000.00, 'Hoàn thành'),
('HD005', 2, 'C005', 'NV002', '2026-05-01', 2100000000.00, 'Chờ xử lý'),
('HD006', 3, 'C002', 'NV003', '2026-05-02', 750000000.00, 'Chờ xử lý'),
('HD007', 1, 'C001', 'NV001', '2026-05-08', 3333333333.00, 'Hoàn thành'),
('HD008', 1, 'C001', 'NV001', '2026-05-11', 55555555.00, 'Chờ xử lý'),
('HD009', 7, 'C001', 'NV001', '2026-05-11', 666666666.00, 'Chờ xử lý'),
('HD010', 8, 'C001', 'NV001', '2026-05-11', 3333.00, 'Chờ xử lý');

--
-- Bẫy `orders`
--
DELIMITER $$
CREATE TRIGGER `trg_after_delete_order` AFTER DELETE ON `orders` FOR EACH ROW BEGIN
    UPDATE employees
    SET cars_sold = cars_sold - 1,
        revenue_total = revenue_total - OLD.order_value,
        commission_val = commission_val - (OLD.order_value * 0.005)
    WHERE employee_id = OLD.employee_id;
    
    UPDATE customers
    SET total_purchased = total_purchased - 1,
        total_spent = total_spent - OLD.order_value
    WHERE customer_id = OLD.customer_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `services`
--

CREATE TABLE `services` (
  `service_id` int(11) NOT NULL,
  `service_name` varchar(100) NOT NULL,
  `price` decimal(15,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `services`
--

INSERT INTO `services` (`service_id`, `service_name`, `price`) VALUES
(1, 'Thay nhớt', 500000.00),
(2, 'Kiểm tra tổng quát', 1000000.00),
(3, 'Rửa xe cao cấp', 200000.00),
(4, 'Cân chỉnh động cơ', 1500000.00),
(5, 'Thay lốp xe', 4500000.00),
(6, 'Bảo dưỡng định kỳ', 2500000.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `service_logs`
--

CREATE TABLE `service_logs` (
  `log_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `car_name` varchar(100) DEFAULT NULL,
  `service_id` int(11) DEFAULT NULL,
  `log_date` date DEFAULT NULL,
  `total_pay` decimal(15,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `service_logs`
--

INSERT INTO `service_logs` (`log_id`, `customer_id`, `car_name`, `service_id`, `log_date`, `total_pay`) VALUES
(1, 1, 'Toyota Camry', 1, '2026-04-15', 500000.00),
(2, 2, 'Honda CR-V', 2, '2026-04-20', 1000000.00),
(3, 1, 'Ford Ranger', 6, '2026-04-28', 2500000.00),
(4, 4, 'Mazda CX-5', 3, '2026-04-30', 200000.00),
(5, 6, 'Mercedes C300', 1, '2026-05-08', 500000.00),
(6, 1, 'Toyota Camry', 1, '2026-05-08', 500000.00);

--
-- Bẫy `service_logs`
--
DELIMITER $$
CREATE TRIGGER `trg_update_customer_spending` AFTER INSERT ON `service_logs` FOR EACH ROW BEGIN
    UPDATE customers 
    SET total_spent = total_spent + NEW.total_pay
    WHERE customer_id = NEW.customer_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'admin',
  `employee_id` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `employee_id`) VALUES
(1, 'admin', '123', 'admin', NULL),
(5, 'a', '123', 'sales', 'NV001');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`appointment_id`),
  ADD KEY `fk_appt_customer` (`customer_id`),
  ADD KEY `fk_appt_car` (`car_id`);

--
-- Chỉ mục cho bảng `brands`
--
ALTER TABLE `brands`
  ADD PRIMARY KEY (`brand_id`),
  ADD UNIQUE KEY `brand_name` (`brand_name`);

--
-- Chỉ mục cho bảng `cars`
--
ALTER TABLE `cars`
  ADD PRIMARY KEY (`car_id`),
  ADD KEY `fk_car_brand` (`brand`),
  ADD KEY `idx_cars_price` (`price_val`),
  ADD KEY `idx_cars_status` (`status`),
  ADD KEY `idx_cars_brand` (`brand`);

--
-- Chỉ mục cho bảng `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`),
  ADD KEY `idx_customers_phone` (`phone`);

--
-- Chỉ mục cho bảng `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`);

--
-- Chỉ mục cho bảng `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `car_id` (`car_id`),
  ADD KEY `employee_id` (`employee_id`),
  ADD KEY `idx_orders_date` (`order_date`),
  ADD KEY `idx_orders_status` (`status`),
  ADD KEY `idx_orders_customer` (`customer_id`);

--
-- Chỉ mục cho bảng `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`service_id`);

--
-- Chỉ mục cho bảng `service_logs`
--
ALTER TABLE `service_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `service_id` (`service_id`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `fk_user_employee` (`employee_id`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `appointments`
--
ALTER TABLE `appointments`
  MODIFY `appointment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT cho bảng `brands`
--
ALTER TABLE `brands`
  MODIFY `brand_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT cho bảng `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT cho bảng `services`
--
ALTER TABLE `services`
  MODIFY `service_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `service_logs`
--
ALTER TABLE `service_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `fk_appt_car` FOREIGN KEY (`car_id`) REFERENCES `cars` (`car_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_appt_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `cars`
--
ALTER TABLE `cars`
  ADD CONSTRAINT `fk_car_brand` FOREIGN KEY (`brand`) REFERENCES `brands` (`brand_id`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`car_id`) REFERENCES `cars` (`car_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
