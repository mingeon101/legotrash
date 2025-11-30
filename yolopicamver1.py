import cv2
import numpy as np
from ultralytics import YOLO
import time
import os # 파일 존재 여부 및 변경 확인을 위해 os 모듈 추가

# --- [사용자 설정] ---
# 처리할 이미지 파일의 경로를 여기에 지정하세요.
IMAGE_PATH = "path/to/your/image.jpg" 
# --------------------

# 1. 모델 로드 및 감지할 클래스 인덱스 설정
model = YOLO("yolov8n.pt")
# 사람(0)과 신호등(9)의 클래스 인덱스를 모두 포함하여 감지합니다.
detection_classes = [0, 9]

def determine_light_color(crop_img):
    """
    잘라낸 신호등 영역의 픽셀별 BGR 값을 분석하여 색깔을 결정합니다.
    """
    if crop_img is None or crop_img.size == 0:
        return "Not Found"

    # BGR 평균값 계산 (OpenCV의 BGR 순서를 가정)
    mean_bgr = cv2.mean(crop_img)
    B = mean_bgr[0]
    G = mean_bgr[1]
    R = mean_bgr[2]
    
    # 픽셀의 전체 밝기 (intensity)
    intensity = R + G + B
    
    debug_rgb = f"R={R:.1f}, G={G:.1f}, B={B:.1f}, Int={intensity:.1f}"

    # 1. 'Dim/Off' 필터
    if intensity < 40:  
        return f"⚫ Dim/Off ({debug_rgb})"

    # 2. 🔴 빨간불 인식 로직
    if (R * 2 > B + G - 10): 
        return f"🔴 Red/Stop ({debug_rgb})"

    # 3. 🚶 파란불 (청록색 계열, 보행자 신호) 인식 로직
    elif (B > R) and (B > G):
        return f"🚶 Blue/Walk ({debug_rgb})"

    # 4. 기타: Unknown으로 처리
    else:
        return f"⚫ Unknown ({debug_rgb})"


print(f"이미지 파일 반복 감지 모드 시작. 대상 경로: {IMAGE_PATH}")
print("'q' 키를 누르면 종료됩니다.")

# 2. 이미지 파일 반복 처리 루프
while True:
    # ⬅️ [핵심 변경] while 루프 내에서 파일을 반복해서 로드
    frame = cv2.imread(IMAGE_PATH) 

    if frame is None:
        if not os.path.exists(IMAGE_PATH):
             print(f"경고: 파일({IMAGE_PATH})을 찾을 수 없습니다. 1초 후 재시도합니다.")
        else:
             print(f"경고: 파일을 읽는 데 실패했습니다. 파일이 손상되었거나 접근 권한이 없습니다. 1초 후 재시도합니다.")
        # 파일이 없거나 읽을 수 없으면 1초 대기 후 다시 루프 시작
        if cv2.waitKey(1000) & 0xFF == ord('q'):
             break
        continue
    
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
    cv2.imshow('YOLOv8 Traffic Light & Person Detection (File Watcher Mode)', frame)

    # ⬅️ 100ms(0.1초) 대기하며 'q' 키 입력 확인. 필요 시 time.sleep()으로 대기 시간을 추가할 수 있음.
    # cv2.waitKey(1)의 대기 시간이 곧 파일 재확인 주기입니다.
    # 여기서는 1ms로 두어 빠른 반응을 유지하고, 필요하면 time.sleep(0.5) 등으로 주기 조절
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # 파일 변경 속도를 늦추고 싶다면 여기서 time.sleep()을 사용하세요. (예: 0.5초 대기)
    time.sleep(0.5) 

# 7. 자원 해제
cv2.destroyAllWindows()
