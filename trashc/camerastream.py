from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time

# Flask ���ø����̼� �ʱ�ȭ
app = Flask(__name__)

# Picamera2 ��ü �ʱ�ȭ �� ���� (�۷ι� ������ ����)
# BGR888 ������ OpenCV�� NumPy �迭�� JPEG���� ���ڵ��ϴ� �� �����մϴ�.
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(preview_config)
picam2.start()

# ī�޶� ���־�
time.sleep(2) 

def generate_frames():
    """
    ī�޶󿡼� �������� �о�� MJPEG �������� ���ڵ��Ͽ� yield �ϴ� ������ �Լ�
    """
    try:
        while True:
            # 1. Picamera2���� NumPy �迭�� ������ ĸó
            frame = picam2.capture_array() 
            
            # 2. OpenCV�� ����Ͽ� JPEG���� ���ڵ�
            # 90�� JPEG ���� ǰ�� (0-100)
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            frame_bytes = buffer.tobytes()

            # 3. MJPEG ��Ʈ���� �������� ������ ���� (yield)
            # '--frame'�� �� �̹��� �������� �������Դϴ�.
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
    except Exception as e:
        print(f"��Ʈ���� ���� �߻�: {e}")
        # ���� �߻� �� ī�޶� �ڿ� ����
        picam2.stop()

@app.route('/video_feed')
def video_feed():
    """
    MJPEG ��Ʈ������ ���� Flask ���Ʈ
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """
    ��Ʈ���� ������ ǥ���� �⺻ HTML ������
    """
    # HTML �� <img src="/video_feed"> �±װ� ��Ʈ���� URL�� ��û�մϴ�.
    return '''
    <html>
        <head>
            <title>Raspberry Pi Stream</title>
        </head>
        <body>
            <h1>Live Pi Camera Stream</h1>
            <img src="/video_feed">
        </body>
    </html>
    '''

if __name__ == '__main__':
    # �ܺ� ������ ����ϱ� ���� host='0.0.0.0' ����
    app.run(host='0.0.0.0', port=5000, debug=False)