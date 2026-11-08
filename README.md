# Xe ESP32 điều khiển qua Wi-Fi + dò line

Code MicroPython cho xe robot dùng ESP32, driver động cơ L298N và 5 cảm biến dò line TCRT5000.

## Tính năng
- ESP32 tự phát Wi-Fi (Access Point) và chạy web server ở cổng 80.
- **Chế độ thủ công:** điều khiển tiến / lùi / trái / phải / dừng bằng các nút trên trình duyệt điện thoại.
- **Chế độ dò line:** xe tự chạy theo vạch đen nhờ 5 cảm biến hồng ngoại.
- Thanh trượt chỉnh tốc độ từ 0 đến 255.

## Sơ đồ chân

| Linh kiện | Chân ESP32 |
|---|---|
| L298N IN1, IN2, ENA (động cơ trái) | 12, 14, 13 |
| L298N IN3, IN4, ENB (động cơ phải) | 27, 26, 25 |
| Cảm biến S1 → S5 (từ trái sang phải) | 15, 2, 4, 16, 17 |

## Cách dùng
1. Nạp firmware MicroPython cho ESP32.
2. Chép `main.py` vào ESP32 (ví dụ bằng Thonny hoặc `mpremote cp main.py :`).
3. Khởi động lại ESP32, kết nối điện thoại vào Wi-Fi `ESP32_RC_Car` (mật khẩu `password123`).
4. Mở trình duyệt và vào địa chỉ `http://192.168.4.1`.
