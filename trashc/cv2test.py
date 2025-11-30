import cv2
from picamera2 import Picamera2
import time
import sys
import numpy as np

# Picamera2 ��ü ���� �� ����
picam2 = Picamera2()

# ���� ��Ʈ�� �ػ� ���� (�̸����� �� OpenCV ó����)
# Full HD 1080p �ػ󵵷� �����մϴ�.
config = picam2.create_video_configuration(main={"size": (1920, 1080), "format": "RGB888"})
picam2.configure(config)

# ������ �̸� ����
WINDOW_NAME = "RPi Camera Live Feed (Press 'q' to exit)"

try:
    # ī�޶� ����
    picam2.start()
    
    # ������ ����
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    print(f"? ī�޶� ����. â�� �������� '{WINDOW_NAME}' â�� Ȱ��ȭ�� ���¿��� 'q'�� ��������.")
    
    # �ǽð� ����
    while True:
        # 1. Picamera2�κ��� ������ ĸó
        # capture_array()�� NumPy �迭 ���·� �̹����� �����ɴϴ�.
        frame_array = picam2.capture_array()
        
        # 2. OpenCV�� ȭ�鿡 ǥ��
        # BGR888 ������ ��������Ƿ� �ٷ� ǥ�� �����մϴ�.
        cv2.imshow(WINDOW_NAME, frame_array)
        
        # 3. ���� ���� Ȯ��
        # 'q' Ű�� �����ų� â�� ������ ������ �����մϴ�.
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break
            
except Exception as e:
    print(f"\n? ���� �߻�: {e}")
    sys.exit(1)
    
finally:
    # ��� ���� �� ����
    if picam2.started:
        picam2.stop()
        picam2.close()
    
    # OpenCV â ��� �ݱ�
    cv2.destroyAllWindows()
    print("���α׷� ���� �� ��� â �ݱ� �Ϸ�.")