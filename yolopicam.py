import cv2
import numpy as np
from ultralytics import YOLO
from picamera2 import Picamera2 # ⬅️ Raspberry Pi 카메라를 위한 라이브러리 추가

# 1. 모델 로드 및 감지할 클래스 인덱스 설정
model = YOLO("yolov8n.pt")
# 사람(0)과 신호등(9)의 클래스 인덱스를 모두 포함하여 감지합니다.
detection_classes = [0, 9]

def determine_light_color(crop_img):
    """
    잘라낸 신호등 영역의 픽셀별 RGB 값을 분석하여 색깔을 결정합니다.
    """
    if crop_img is None or crop_img.size == 0:
        return "Not Found"

    # BGR 평균값 계산
    mean_bgr = cv2.mean(crop_img)
    B = mean_bgr[0]
    G = mean_bgr[1]
    R = mean_bgr[2]
    
    # 픽셀의 전체 밝기 (intensity)
    intensity = R + G + B
    
    # 디버깅을 위해 RGB 값과 intensity를 문자열로 반환
    debug_rgb = f"R={R:.1f}, G={G:.1f}, B={B:.1f}, Int={intensity:.1f}"

    # 1. 'Dim/Off' 필터
    if intensity < 40: 
        return f"⚫ Dim/Off ({debug_rgb})"

    # 2. 🔴 빨간불 인식 로직
    # R * 2 > B + G - 10
    if (R * 2 > B + G - 10): 
        return f"🔴 Red/Stop ({debug_rgb})"

    # 3. 🚶 파란불 (청록색 계열, 보행자 신호) 인식 로직
    elif (B > R) and (B > G):
        return f"🚶 Blue/Walk ({debug_rgb})"

    # 4. 기타: Unknown으로 처리
    else:
        # 여기에 초록불 인식 로직 (G > R and G > B)를 추가하면 더 정확해집니다.
        return f"⚫ Unknown ({debug_rgb})"


# 2. Picamera2 객체 초기화 및 설정 (웹캠 캡처 객체 대체)
try:
    picam2 = Picamera2()
    # 고해상도 설정을 위한 configuration
    # YOLO 추론 속도를 위해 낮은 해상도(예: 640x480)를 사용하는 것이 좋습니다.
    picam2.preview_configuration.main.size = (640, 480) 
    picam2.preview_configuration.main.format = "RGB888" # BGR 대신 RGB888 포맷 사용
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    print("Raspberry Pi 카메라를 시작합니다. 'q' 키를 누르면 종료됩니다.")
    
except Exception as e:
    print(f"오류: Picamera2 초기화 실패. 카메라가 연결되어 있고 라이브러리가 설치되었는지 확인하세요. 오류: {e}")
    exit()

# 3. 실시간 프레임 처리 루프
while True:
    # ⬅️ Picamera2로부터 프레임 캡처 (NumPy 배열)
    frame = picam2.capture_array()
    
    # Picamera2는 기본적으로 RGB 포맷을 반환하므로,
    # OpenCV의 BGR 포맷에 맞추기 위해 변환합니다.
    # determine_light_color 함수는 BGR 순서를 가정하고 있습니다.
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # YOLOv8 추론 실행
    results = model.predict(
        source=frame, 
        classes=detection_classes, 
        conf=0.25,
        verbose=False 
    )

    # 4. 감지된 객체 처리 루프
    for r in results:
        boxes = r.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf[0]
            cls_id = int(box.cls[0]) 

            label = ""
            box_color = (0, 0, 0)
            
            if cls_id == 9: # 신호등인 경우 (클래스 ID 9)
                # 신호등 영역 잘라내기
                x1_crop = max(0, x1)
                y1_crop = max(0, y1)
                x2_crop = min(frame.shape[1], x2)
                y2_crop = min(frame.shape[0], y2)
                
                if x2_crop > x1_crop and y2_crop > y1_crop:
                    # BGR 순서로 잘라내기
                    cropped_traffic_light = frame[y1_crop:y2_crop, x1_crop:x2_crop] 
                    detected_color = determine_light_color(cropped_traffic_light)
                else:
                    detected_color = "Invalid Crop"
                
                label = f"Light: {detected_color} ({confidence:.2f})"
                box_color = (255, 0, 0) # 파란색 박스 (BGR)
                
            elif cls_id == 0: # 사람인 경우 (클래스 ID 0)
                label = f"Person ({confidence:.2f})"
                box_color = (0, 255, 0) # 초록색 박스 (BGR)
                
            else:
                continue 

            # 5. 감지 결과를 프레임에 표시
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - h - 10), (x1 + w, y1), box_color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 6. 처리된 프레임을 화면에 표시
    cv2.imshow('YOLOv8 Traffic Light & Person Detection (Picamera2)', frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 7. 자원 해제
picam2.stop() # ⬅️ picamera2 객체 중지
cv2.destroyAllWindows()
