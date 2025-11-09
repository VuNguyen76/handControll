import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Tắt fail-safe của pyautogui
pyautogui.FAILSAFE = False

# Khởi tạo MediaPipe Hand
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Lấy kích thước màn hình
screen_width, screen_height = pyautogui.size()

# Cấu hình
class Config:
    SMOOTH_FACTOR = 2
    CLICK_THRESHOLD = 40
    DOUBLE_CLICK_TIME = 0.5
    SCROLL_THRESHOLD = 50
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.7
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    # Mở rộng vùng di chuyển để đến được mọi góc màn hình
    FRAME_MARGIN = 100  # Pixel mở rộng

class HandGesture:
    def __init__(self):
        self.prev_x = 0
        self.prev_y = 0
        self.last_click_time = 0
        self.click_count = 0
        self.is_clicking = False
        self.prev_fingers_up = []
        
    def get_distance(self, point1, point2):
        """Tính khoảng cách giữa 2 điểm"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def get_finger_status(self, hand_landmarks, frame_width, frame_height):
        """Kiểm tra ngón tay nào đang giơ lên"""
        fingers_up = []
        
        # Ngón cái
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]
        if thumb_tip.x < thumb_ip.x:  # Tay phải
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        # 4 ngón còn lại
        finger_tips = [8, 12, 16, 20]  # Ngón trỏ, giữa, áp út, út
        finger_pips = [6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        return fingers_up
    
    def move_mouse(self, index_x, index_y, frame_width, frame_height):
        """Di chuyển chuột với vùng mở rộng"""
        # Mở rộng vùng mapping để đến được mọi góc màn hình
        screen_x = np.interp(index_x, 
                            [-Config.FRAME_MARGIN, frame_width + Config.FRAME_MARGIN], 
                            [0, screen_width])
        screen_y = np.interp(index_y, 
                            [-Config.FRAME_MARGIN, frame_height + Config.FRAME_MARGIN], 
                            [0, screen_height])
        
        # Làm mượt chuyển động
        current_x = self.prev_x + (screen_x - self.prev_x) / Config.SMOOTH_FACTOR
        current_y = self.prev_y + (screen_y - self.prev_y) / Config.SMOOTH_FACTOR
        
        # Đảm bảo không vượt quá màn hình
        current_x = max(0, min(screen_width - 1, current_x))
        current_y = max(0, min(screen_height - 1, current_y))
        
        pyautogui.moveTo(current_x, current_y)
        
        self.prev_x, self.prev_y = current_x, current_y
        return int(current_x), int(current_y)
    
    def handle_click(self, distance):
        """Xử lý click chuột (đơn và đúp)"""
        current_time = time.time()
        
        if distance < Config.CLICK_THRESHOLD:
            if not self.is_clicking:
                self.is_clicking = True
                
                # Kiểm tra double click
                if current_time - self.last_click_time < Config.DOUBLE_CLICK_TIME:
                    self.click_count += 1
                    if self.click_count == 1:
                        pyautogui.doubleClick()
                        return "DOUBLE CLICK"
                else:
                    self.click_count = 0
                    pyautogui.click()
                    
                self.last_click_time = current_time
                return "CLICK"
        else:
            self.is_clicking = False
            self.click_count = 0
        
        return None
    
    def handle_right_click(self, thumb_pos, middle_pos):
        """Click chuột phải: Ngón cái chạm ngón giữa"""
        distance = self.get_distance(thumb_pos, middle_pos)
        if distance < Config.CLICK_THRESHOLD:
            pyautogui.rightClick()
            time.sleep(0.3)
            return True
        return False
    
    def handle_scroll(self, fingers_up, index_y):
        """Cuộn chuột: Giơ 2 ngón (trỏ + giữa)"""
        # Chỉ giơ ngón trỏ và ngón giữa
        if fingers_up == [0, 1, 1, 0, 0]:
            if hasattr(self, 'scroll_start_y'):
                delta = self.scroll_start_y - index_y
                if abs(delta) > Config.SCROLL_THRESHOLD:
                    scroll_amount = int(delta / 10)
                    pyautogui.scroll(scroll_amount)
                    self.scroll_start_y = index_y
                    return f"SCROLL {scroll_amount}"
            else:
                self.scroll_start_y = index_y
        else:
            if hasattr(self, 'scroll_start_y'):
                delattr(self, 'scroll_start_y')
        
        return None

def draw_info(frame, info_text, position, color=(255, 255, 255)):
    """Vẽ thông tin lên frame"""
    cv2.putText(frame, info_text, position, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def draw_instructions(frame):
    """Vẽ hướng dẫn sử dụng"""
    instructions = [
        "1 ngon (tro): Di chuyen chuot",
        "Tro + Cai: Click trai",
        "Giua + Cai: Click phai", 
        "2 ngon (tro+giua): Cuon chuot",
        "Nhan 'q': Thoat"
    ]
    
    y_offset = 30
    for i, text in enumerate(instructions):
        draw_info(frame, text, (10, y_offset + i * 30), (0, 255, 255))

def main():
    """Hàm chính"""
    cap = cv2.VideoCapture(0)
    cap.set(3, Config.CAMERA_WIDTH)
    cap.set(4, Config.CAMERA_HEIGHT)
    
    gesture = HandGesture()
    
    print("=" * 60)
    print("CHUONG TRINH DIEU KHIEN CHUOT BANG TAY")
    print("=" * 60)
    print("Huong dan:")
    print("  - 1 ngon tro: Di chuyen chuot")
    print("  - Ngon tro + ngon cai: Click trai (nhanh 2 lan = double click)")
    print("  - Ngon giua + ngon cai: Click phai")
    print("  - 2 ngon (tro + giua): Cuon chuot len/xuong")
    print("  - Nhan 'q': Thoat chuong trinh")
    print("=" * 60)
    
    with mp_hands.Hands(
        min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE,
        max_num_hands=1
    ) as hands:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Khong the doc tu camera")
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            frame_height, frame_width, _ = frame.shape
            action_text = ""
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Vẽ bàn tay
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Lấy tọa độ các ngón
                    index_tip = hand_landmarks.landmark[8]
                    index_x = int(index_tip.x * frame_width)
                    index_y = int(index_tip.y * frame_height)
                    
                    thumb_tip = hand_landmarks.landmark[4]
                    thumb_x = int(thumb_tip.x * frame_width)
                    thumb_y = int(thumb_tip.y * frame_height)
                    
                    middle_tip = hand_landmarks.landmark[12]
                    middle_x = int(middle_tip.x * frame_width)
                    middle_y = int(middle_tip.y * frame_height)
                    
                    # Kiểm tra ngón tay nào đang giơ
                    fingers_up = gesture.get_finger_status(hand_landmarks, frame_width, frame_height)
                    
                    # Chế độ di chuyển chuột (chỉ giơ ngón trỏ)
                    if fingers_up == [0, 1, 0, 0, 0]:
                        mouse_x, mouse_y = gesture.move_mouse(index_x, index_y, frame_width, frame_height)
                        action_text = f"DI CHUYEN ({mouse_x}, {mouse_y})"
                        cv2.circle(frame, (index_x, index_y), 15, (0, 255, 0), -1)
                        
                        # Click trái: Ngón trỏ + Ngón cái
                        distance_thumb_index = gesture.get_distance(
                            (thumb_x, thumb_y), (index_x, index_y)
                        )
                        click_result = gesture.handle_click(distance_thumb_index)
                        if click_result:
                            action_text = click_result
                            cv2.line(frame, (index_x, index_y), (thumb_x, thumb_y), (0, 0, 255), 3)
                    
                    # Click phải: Ngón giữa + Ngón cái
                    elif fingers_up == [0, 0, 1, 0, 0] or fingers_up == [1, 0, 1, 0, 0]:
                        if gesture.handle_right_click((thumb_x, thumb_y), (middle_x, middle_y)):
                            action_text = "RIGHT CLICK"
                            cv2.line(frame, (middle_x, middle_y), (thumb_x, thumb_y), (255, 0, 255), 3)
                    
                    # Cuộn chuột: 2 ngón (trỏ + giữa)
                    scroll_result = gesture.handle_scroll(fingers_up, index_y)
                    if scroll_result:
                        action_text = scroll_result
                        cv2.circle(frame, (index_x, index_y), 15, (255, 255, 0), -1)
                        cv2.circle(frame, (middle_x, middle_y), 15, (255, 255, 0), -1)
                    
                    # Vẽ các điểm quan trọng
                    cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 0), -1)
            
            # Hiển thị thông tin
            draw_instructions(frame)
            if action_text:
                draw_info(frame, action_text, (10, frame_height - 30), (0, 255, 0))
            
            # Hiển thị frame
            cv2.imshow('Hand Mouse Control', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
