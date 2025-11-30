import time
import base64
import json
import requests
import numpy as np
import cv2
from picamera2 import Picamera2

# --- 1. ���� ���� ---
FIREBASE_URL = "https://rhkdrh-default-rtdb.firebaseio.com/camera_data.json" # �����͸� ������ ���
INTERVAL_SECONDS = 0.1 # �̹��� ĸó �� ���� ���� (30��)

# --- 2. Picamera2 �ʱ�ȭ ---
try:
    picam2 = Picamera2()
    # ĸó ������ ���� �ּ����� �ػ󵵷� ���� (Base64 ���ڵ� ũ�� ���� ����)
    capture_config = picam2.create_still_configuration(
        main={"size": (320, 240), "format": "RGB888"}
    )
    picam2.configure(capture_config)
    picam2.start()
    time.sleep(2)  # ī�޶� ���־�
    print("? ī�޶� ��Ʈ���� ����.")
except Exception as e:
    print(f"? Picamera2 �ʱ�ȭ ����: {e}")
    exit()


def encode_frame_to_base64():
    """ī�޶󿡼� �������� ĸó�ϰ� Base64 ���ڿ��� ���ڵ��մϴ�."""
    # 1. ������ ĸó (NumPy �迭)
    frame = picam2.capture_array()
    
    # 2. JPEG ���� �� ���ڵ� (Base64 ũ�⸦ ���̴� �� �ʼ�)
    # IMWRITE_JPEG_QUALITY: 0-100. 80���� �����Ͽ� ǰ���� ũ�� Ÿ��
    success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    
    if not success:
        print("? JPEG ���ڵ� ����.")
        return None
        
    # 3. Base64�� ���� ���ڵ�
    base64_encoded_data = base64.b64encode(buffer).decode('utf-8')
    return base64_encoded_data

def upload_to_firebase(base64_data):
    """Base64 �����͸� Firebase Realtime Database�� �����մϴ�."""
    # ���� Ű ������ ���� ���� Ÿ�ӽ������� ���
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Firebase�� ������ ������ ����
    payload = {
        "timestamp": timestamp,
        "image_base64": base64_data,
        "size_kb": len(base64_data) / 1024 # ũ�� Ȯ�ο�
    }
    
    # Firebase REST API�� POST�� ����Ͽ� �� ��带 �߰��մϴ�.
    try:
        response = requests.post(FIREBASE_URL, json=payload)
        response.raise_for_status() # HTTP ������ �߻��ϸ� ���� �߻�
        
        print(f"? [{timestamp}] Firebase ���� ����. ũ��: {len(base64_data) / 1024:.2f} KB")
        return True
    except requests.exceptions.RequestException as e:
        print(f"? Firebase ��û ����: {e}")
        print("   URL �� ���� ������ Ȯ���ϼ���.")
        return False

# --- 3. ���� ���� ���� ---
if __name__ == "__main__":
    try:
        while True:
            start_time = time.time()
            
            # 1. Base64 ���ڵ� ����
            base64_image = encode_frame_to_base64()
            
            if base64_image:
                # 2. Firebase ���ε�
                upload_to_firebase(base64_image)
            
            # 3. ���� ������� ��� �ð� ���
            elapsed_time = time.time() - start_time
            sleep_time = INTERVAL_SECONDS - elapsed_time
            
            if sleep_time > 0:
                print(f"   ���� ĸó���� {sleep_time:.2f}�� ���...")
                time.sleep(sleep_time)
            else:
                print("   ���: ĸó �� ���ε� �ð��� 30�ʸ� �ʰ��߽��ϴ�!")

    except KeyboardInterrupt:
        print("\n���α׷� ����.")
    finally:
        picam2.stop()
        print("ī�޶� �ڿ� ���� �Ϸ�.")