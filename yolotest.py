from ultralytics import YOLO
import cv2
import numpy as np

# 1. 모델 로드 및 감지할 클래스 인덱스 설정
model = YOLO("yolov8n.pt")
# 사람(0)과 신호등(9)의 클래스 인덱스를 모두 포함하여 감지합니다.
detection_classes = [0, 9] 

def determine_light_color(crop_img):
    """
    잘라낸 신호등 영역의 픽셀별 RGB 값을 분석하여 색깔을 결정합니다.
    (이전 절대값 기반 로직으로 복원)
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

    # 1. 'Dim/Off' 필터: 전체 밝기가 40 미만일 때 Dim/Off 처리 (이전 최종 조정 값 유지)
    if intensity < 40: 
        return f"⚫ Dim/Off ({debug_rgb})"

    # 2. 🔴 빨간불 인식 로직 (이전 절대값 로직으로 복원)
    # R*2 > B+G-20: R값이 G와 B의 합의 절반보다 10만큼 높을 때 빨간불로 판단합니다.
    if (R * 2 > B + G - 10): 
        return f"🔴 Red/Stop ({debug_rgb})"

    # 3. 🚶 파란불 (청록색 계열) 인식 로직 (이전 절대값 로직으로 복원)
    # B 값이 R과 G 값보다 절대적으로 높을 때 파란불로 판단합니다.
    elif (B > R) and (B > G):
        return f"🚶 Blue/Walk ({debug_rgb})"

    # 4. 기타: 위에 해당하지 않는 모든 경우 
    else:
        return f"⚫ Unknown ({debug_rgb})"

# 2. 웹캠 캡처 객체 및 루프
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("오류: 웹캠을 열 수 없습니다.")
    exit()

print("웹캠을 시작합니다. 'q' 키를 누르면 종료됩니다.")

# 3. 실시간 프레임 처리 루프
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv8 추론 실행: 사람(0)과 신호등(9)을 모두 감지합니다.
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
            cls_id = int(box.cls[0]) # 클래스 ID 추출 (0 또는 9)

            label = ""
            
            if cls_id == 9: # 신호등인 경우 (클래스 ID 9)
                # 신호등 영역 잘라내기
                x1_crop = max(0, x1)
                y1_crop = max(0, y1)
                x2_crop = min(frame.shape[1], x2)
                y2_crop = min(frame.shape[0], y2)
                
                if x2_crop > x1_crop and y2_crop > y1_crop:
                    cropped_traffic_light = frame[y1_crop:y2_crop, x1_crop:x2_crop]
                    detected_color = determine_light_color(cropped_traffic_light)
                else:
                    detected_color = "Invalid Crop"
                
                label = f"Light: {detected_color} ({confidence:.2f})"
                box_color = (255, 0, 0) # 신호등은 파란색 박스
                
            elif cls_id == 0: # 사람인 경우 (클래스 ID 0)
                label = f"Person ({confidence:.2f})"
                box_color = (0, 255, 0) # 사람은 초록색 박스
                
            else:
                continue # 다른 객체는 무시

            # 5. 감지 결과를 프레임에 표시
            
            # 바운딩 박스 그리기
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            
            # 텍스트 배경 및 출력
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - h - 10), (x1 + w, y1), box_color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 6. 처리된 프레임을 화면에 표시
    cv2.imshow('YOLOv8 Traffic Light & Person Detection (Absolute Logic)', frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 7. 자원 해제
cap.release()
cv2.destroyAllWindows()
