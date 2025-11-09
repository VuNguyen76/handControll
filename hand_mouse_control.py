import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Tắt fail-safe của pyautogui để tránh lỗi khi di chuyển chuột ra góc màn hình
pyautogui.FAILSAFE = False

# Khởi tạo MediaPipe Hand
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Lấy kích thước màn hình
screen_width, screen_height = pyautogui.size()

# Khởi tạo camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Chiều rộng
cap.set(4, 480)  # Chiều cao

# Biến để làm mượt chuyển động chuột
smooth_factor = 5
prev_x, prev_y = 0, 0

# Biến để phát hiện click và kéo thả
click_threshold = 40  # Khoảng cách giữa ngón trỏ và ngón cái để click
is_dragging = False  # Trạng thái đang kéo thả

print("Hướng dẫn sử dụng:")
print("- Giơ ngón trỏ lên để di chuyển chuột")
print("- Chạm ngón trỏ và ngón cái lại gần nhau để click chuột trái")
print("- Giữ ngón trỏ và ngón cái chạm nhau rồi di chuyển để kéo thả")
print("- Nhấn 'q' để thoát chương trình")

with mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
) as hands:
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Không thể đọc từ camera")
            break
        
        # Lật ảnh theo chiều ngang để có hiệu ứng gương
        frame = cv2.flip(frame, 1)
        
        # Chuyển đổi BGR sang RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Xử lý ảnh để phát hiện bàn tay
        results = hands.process(rgb_frame)
        
        frame_height, frame_width, _ = frame.shape
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Vẽ bàn tay lên frame
                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
                
                # Lấy tọa độ ngón trỏ (index finger tip - landmark 8)
                index_finger_tip = hand_landmarks.landmark[8]
                index_x = int(index_finger_tip.x * frame_width)
                index_y = int(index_finger_tip.y * frame_height)
                
                # Lấy tọa độ ngón cái (thumb tip - landmark 4)
                thumb_tip = hand_landmarks.landmark[4]
                thumb_x = int(thumb_tip.x * frame_width)
                thumb_y = int(thumb_tip.y * frame_height)
                
                # Chuyển đổi tọa độ từ camera sang tọa độ màn hình
                screen_x = np.interp(index_x, [0, frame_width], [0, screen_width])
                screen_y = np.interp(index_y, [0, frame_height], [0, screen_height])
                
                # Làm mượt chuyển động
                current_x = prev_x + (screen_x - prev_x) / smooth_factor
                current_y = prev_y + (screen_y - prev_y) / smooth_factor
                
                # Di chuyển chuột
                pyautogui.moveTo(current_x, current_y)
                
                prev_x, prev_y = current_x, current_y
                
                # Tính khoảng cách giữa ngón trỏ và ngón cái
                distance = np.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
                
                # Vẽ đường nối giữa ngón trỏ và ngón cái
                cv2.line(frame, (index_x, index_y), (thumb_x, thumb_y), (0, 255, 0), 2)
                cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), -1)
                cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 0), -1)
                
                # Xử lý kéo thả (drag and drop)
                if distance < click_threshold:
                    if not is_dragging:
                        # Bắt đầu kéo - nhấn giữ chuột
                        pyautogui.mouseDown()
                        is_dragging = True
                        cv2.putText(frame, "DRAGGING...", (50, 100), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 165, 255), 3)
                    else:
                        # Đang kéo
                        cv2.putText(frame, "DRAGGING...", (50, 100), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 165, 255), 3)
                else:
                    if is_dragging:
                        # Thả chuột khi ngón tay rời xa nhau
                        pyautogui.mouseUp()
                        is_dragging = False
                        cv2.putText(frame, "DROPPED!", (50, 100), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                
                # Hiển thị khoảng cách
                cv2.putText(frame, f"Distance: {int(distance)}", (50, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Hiển thị frame
        cv2.imshow('Hand Mouse Control', frame)
        
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
