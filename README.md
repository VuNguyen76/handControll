# Điều Khiển Chuột Bằng Ngón Tay

Chương trình Python cho phép bạn điều khiển chuột máy tính bằng cách sử dụng webcam và nhận diện bàn tay.

## Tính năng

- **Di chuyển chuột**: Sử dụng ngón trỏ để di chuyển con trỏ chuột
- **Click chuột trái**: Chạm ngón trỏ và ngón cái lại gần nhau
- **Hiển thị trực quan**: Xem bàn tay được nhận diện trên màn hình

## Cài đặt

1. Cài đặt Python 3.8 trở lên

2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Cách sử dụng

1. Chạy chương trình:

```bash
python hand_mouse_control.py
```

2. Cho phép truy cập camera khi được yêu cầu

3. Điều khiển chuột:

   - Giơ bàn tay trước camera
   - Dùng ngón trỏ để di chuyển con trỏ chuột
   - Chạm ngón trỏ và ngón cái lại gần nhau để click

4. Nhấn phím 'q' để thoát chương trình

## Yêu cầu hệ thống

- Python 3.8+
- Webcam
- Windows/Linux/MacOS

## Thư viện sử dụng

- **OpenCV**: Xử lý hình ảnh từ camera
- **MediaPipe**: Nhận diện bàn tay và các điểm mốc
- **PyAutoGUI**: Điều khiển chuột máy tính
- **NumPy**: Tính toán toán học

## Tùy chỉnh

Bạn có thể điều chỉnh các thông số trong file `hand_mouse_control.py`:

- `smooth_factor`: Độ mượt của chuyển động chuột (mặc định: 5)
- `click_threshold`: Khoảng cách để kích hoạt click (mặc định: 40)
- `min_detection_confidence`: Độ tin cậy phát hiện bàn tay (mặc định: 0.7)

## Lưu ý

- Đảm bảo có đủ ánh sáng để camera nhận diện tốt
- Giữ bàn tay trong khung hình camera
- Tránh di chuyển quá nhanh để chuột hoạt động mượt mà
