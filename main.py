import network
import socket
from machine import Pin, PWM

# === Cấu hình chân điều khiển động cơ (L298N) ===
IN1 = Pin(12, Pin.OUT)  # Điều khiển chiều quay động cơ trái
IN2 = Pin(14, Pin.OUT)
ENA = PWM(Pin(13), freq=5000)  # Cấp xung PWM điều chỉnh tốc độ động cơ trái

IN3 = Pin(27, Pin.OUT)  # Điều khiển chiều quay động cơ phải
IN4 = Pin(26, Pin.OUT)
ENB = PWM(Pin(25), freq=5000)  # Cấp xung PWM điều chỉnh tốc độ động cơ phải

# === Cấu hình 5 cảm biến hồng ngoại dò line (TCRT5000) ===
S1 = Pin(15, Pin.IN)  # Cảm biến ngoài cùng bên trái
S2 = Pin(2, Pin.IN)   # Cảm biến giữa trái
S3 = Pin(4, Pin.IN)   # Cảm biến trung tâm
S4 = Pin(16, Pin.IN)  # Cảm biến giữa phải
S5 = Pin(17, Pin.IN)  # Cảm biến ngoài cùng bên phải

speedVal = 200        # Tốc độ mặc định ban đầu (Dải từ 0-255)
isLineMode = False    # Biến cờ (Flag) xác định chế độ: False = Thủ công, True = Tự động dò line

# === Giao diện điều khiển Web (HTML/CSS/JS) ===
def getHTML():
    # Trả về chuỗi mã HTML, CSS và Javascript để hiển thị bảng điều khiển xe trên trình duyệt.
    # Sử dụng Fetch API để gửi lệnh HTTP ngầm về máy chủ ESP32 mà không cần tải lại trang.
    html = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    html += "<style>body{text-align:center;font-family:Arial,sans-serif;background-color:#222;color:white;} .btn{padding:20px;margin:10px;font-size:30px;border-radius:15px;background-color:#008CBA;color:white;border:none;width:90px;height:90px;box-shadow:0 5px #005f7a;}"
    html += ".btn:active{background-color:#005f7a;box-shadow:0 2px #003f52;transform:translateY(3px);} .mode-btn{width:140px;height:50px;font-size:18px;margin:10px;} .grid{display:grid;grid-template-columns:auto auto auto;justify-content:center;gap:10px;margin-top:20px;} .slider-container{margin-top:20px;} .slider{width:250px;}</style>"
    html += "<script>"
    html += "function sendCmd(cmd, e) { if(e) e.preventDefault(); fetch('/' + cmd); }"
    html += "function setSpeed(val) { fetch('/speed?val=' + val); }"
    html += "</script></head><body>"
    html += "<h2>BẢNG ĐIỀU KHIỂN XE</h2>"
    html += "<div>"
    html += "<button class=\"btn mode-btn\" style=\"background-color:#ff9800;\" onclick=\"sendCmd('manual', event)\">THỦ CÔNG</button>"
    html += "<button class=\"btn mode-btn\" style=\"background-color:#4CAF50;\" onclick=\"sendCmd('line', event)\">DÒ LINE</button>"
    html += "</div>"
    html += "<div class=\"grid\">"
    html += "<div></div><button class=\"btn\" onmousedown=\"sendCmd('forward', event)\" onmouseup=\"sendCmd('stop', event)\" ontouchstart=\"sendCmd('forward', event)\" ontouchend=\"sendCmd('stop', event)\">&#9650;</button><div></div>"
    html += "<button class=\"btn\" onmousedown=\"sendCmd('left', event)\" onmouseup=\"sendCmd('stop', event)\" ontouchstart=\"sendCmd('left', event)\" ontouchend=\"sendCmd('stop', event)\">&#9664;</button>"
    html += "<button class=\"btn\" style=\"background-color:#f44336;box-shadow:0 5px #ba2b20;\" onclick=\"sendCmd('stop', event)\">&#9632;</button>"
    html += "<button class=\"btn\" onmousedown=\"sendCmd('right', event)\" onmouseup=\"sendCmd('stop', event)\" ontouchstart=\"sendCmd('right', event)\" ontouchend=\"sendCmd('stop', event)\">&#9654;</button>"
    html += "<div></div><button class=\"btn\" onmousedown=\"sendCmd('backward', event)\" onmouseup=\"sendCmd('stop', event)\" ontouchstart=\"sendCmd('backward', event)\" ontouchend=\"sendCmd('stop', event)\">&#9660;</button><div></div>"
    html += "</div>"
    html += "<div class=\"slider-container\"><h3>Tốc độ: <input type=\"range\" min=\"0\" max=\"255\" value=\"200\" class=\"slider\" onchange=\"setSpeed(this.value)\"></h3></div>"
    html += "</body></html>"
    return html

# === Các hàm điều khiển động cơ ===

def set_pwm(ena_val, enb_val):
    # Chuyển đổi dải tốc độ từ 0-255 (từ giao diện web) sang duty cycle chuẩn của MicroPython (0-1023).
    # Áp dụng giá trị duty cycle lên 2 chân ENA và ENB để kiểm soát tốc độ của từng động cơ.
    ENA.duty(int(ena_val * 1023 / 255))
    ENB.duty(int(enb_val * 1023 / 255))

def forward():
    # Lệnh điều khiển xe tiến thẳng: 2 bánh cùng quay theo chiều tiến lên.
    IN1.value(0)
    IN2.value(1)
    IN3.value(1)
    IN4.value(0)
    set_pwm(speedVal, speedVal)

def backward():
    # Lệnh điều khiển xe đi lùi: 2 bánh cùng quay theo chiều giật lùi.
    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(1)
    set_pwm(speedVal, speedVal)

def turnLeft():
    # Lệnh xoay trái tại chỗ: Bánh trái quay lùi, bánh phải quay tiến.
    IN1.value(1)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)
    set_pwm(speedVal, speedVal)

def turnRight():
    # Lệnh xoay phải tại chỗ: Bánh trái quay tiến, bánh phải quay lùi.
    IN1.value(0)
    IN2.value(1)
    IN3.value(0)
    IN4.value(1)
    set_pwm(speedVal, speedVal)

def stopCar():
    # Lệnh dừng xe khẩn cấp: Ngắt toàn bộ tín hiệu hướng quay và kéo PWM về 0.
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)
    set_pwm(0, 0)

def moveCustom(speedA, speedB, dirA, dirB):
    # Hàm tùy biến linh hoạt để rẽ mượt trong chế độ dò line.
    # Thông số dirA, dirB (Boolean): Chiều quay của động cơ trái/phải (True = Tiến, False = Lùi).
    # Thông số speedA, speedB: Tốc độ thiết lập riêng biệt cho từng bánh xe để bẻ lái mượt mà.
    IN1.value(0 if dirA else 1)
    IN2.value(1 if dirA else 0)
    IN3.value(1 if dirB else 0)
    IN4.value(0 if dirB else 1)
    set_pwm(speedA, speedB)

# === Thuật toán dò đường (Line Follower) ===

def lineFollowLogic():
    # Đọc trực tiếp mức logic từ 5 mắt cảm biến hồng ngoại.
    # Trả về 1 (True) nếu nhận diện vạch đen, và 0 (False) nếu nhận diện nền trắng.
    s1 = S1.value()
    s2 = S2.value()
    s3 = S3.value()
    s4 = S4.value()
    s5 = S5.value()

    if s1 and s2 and s3 and s4 and s5:
        # Cả 5 mắt đều thấy màu đen (vạch ngang lớn) -> Dừng xe.
        stopCar()
    elif not s1 and not s2 and not s3 and not s4 and not s5:
        # Cả 5 mắt đều thấy nền trắng (đi chệch khỏi track) -> Dừng xe.
        stopCar()
    elif s1 and not s5:
        # Lệch hẳn xe qua bên phải (mắt ngoài cùng bên trái vướng vạch) -> Cua gắt sang trái.
        moveCustom(speedVal, speedVal, True, False)
    elif s5 and not s1:
        # Lệch hẳn xe qua bên trái (mắt ngoài cùng bên phải vướng vạch) -> Cua gắt sang phải.
        moveCustom(speedVal, speedVal, False, True)
    elif s2 and not s4:
        # Hơi chệch sang phải -> Hãm tốc độ bánh phải xuống 30% để nắn xe dần sang trái.
        moveCustom(speedVal, speedVal * 0.3, True, True)
    elif s4 and not s2:
        # Hơi chệch sang trái -> Hãm tốc độ bánh trái xuống 30% để nắn xe dần sang phải.
        moveCustom(speedVal * 0.3, speedVal, True, True)
    elif s3:
        # Mắt cảm biến trung tâm nằm thẳng trên vạch đen -> Tiếp tục lao thẳng phía trước.
        moveCustom(speedVal, speedVal, True, True)
    else:
        # Trường hợp ngoại lệ -> Giữ nguyên hướng đi thẳng.
        moveCustom(speedVal, speedVal, True, True)

# === Thiết lập ESP32 làm Access Point (Phát Wi-Fi) ===
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32_RC_Car", password="password123", authmode=network.AUTH_WPA_WPA2_PSK)

stopCar() # Đảm bảo xe đứng yên khi khởi động

# === Cài đặt Socket Server HTTP ===
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80)) # Lắng nghe trên port 80
s.listen(5)
s.setblocking(False) # Cấu hình non-blocking để không chặn luồng chạy (giúp xe vừa dò line vừa nghe lệnh web)

# === Vòng lặp chính ===
while True:
    # Nếu cờ báo chế độ dò line được bật, hàm dò line sẽ chạy liên tục
    if isLineMode:
        lineFollowLogic()

    try:
        # Chấp nhận kết nối từ trình duyệt/điện thoại
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')

        if request:
            # Tách lấy dòng đầu tiên của HTTP request để tìm đường dẫn
            req_line = request.split('\r\n')[0]
            path = req_line.split(' ')[1]

            # Khởi tạo phản hồi mặc định
            response_header = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n"
            response_body = "OK"

            # Xử lý các đường dẫn tương ứng với nút bấm trên web
            if path == "/":
                response_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
                response_body = getHTML()
            elif path == "/forward":
                isLineMode = False # Tắt dò line nếu bấm chạy tay
                forward()
            elif path == "/backward":
                isLineMode = False
                backward()
            elif path == "/left":
                isLineMode = False
                turnLeft()
            elif path == "/right":
                isLineMode = False
                turnRight()
            elif path == "/stop":
                isLineMode = False
                stopCar()
            elif path == "/line":
                isLineMode = True # Kích hoạt dò line tự động
            elif path == "/manual":
                isLineMode = False
                stopCar()
            elif path.startswith("/speed"):
                # Cắt chuỗi để lấy giá trị tốc độ từ URL
                try:
                    val = int(path.split('val=')[1].split(' ')[0])
                    speedVal = val
                except:
                    pass

            # Trả dữ liệu về client và đóng kết nối
            conn.send(response_header + response_body)
        conn.close()
    except OSError:
        # Bỏ qua lỗi không có client kết nối để tiếp tục chạy vòng lặp dò line
        pass
