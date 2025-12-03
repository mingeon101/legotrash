
import time
import base64
import json
import requests
from picamera import PiCamera # Picamera1 라이브러리 임포트
from io import BytesIO       # 메모리 스트림 사용을 위해 임포트

# --- 1. 환경 설정 ---
# FIREBASE_URL = "https://rhkdrh-default-rtdb.firebaseio.com/camera_data.json" 
# 실제 사용 시, 위의 주석 처리된 URL로 변경해야 합니다.
FIREBASE_URL = "YOUR_FIREBASE_URL" 
# 이미지 캡처 및 업로드 간 최소 간격
INTERVAL_SECONDS = 0.1 

# --- 2. PiCamera 초기화 (Picamera1) ---
try:
    # 해상도 설정 (Base64 크기 제한을 위해 낮은 해상도 권장)
    camera = PiCamera(resolution=(320, 240))
    camera.start_preview()
    time.sleep(2)  # 카메라 워밍업
    print("✅ PiCamera1 스트림 시작 성공.")
except Exception as e:
    print(f"❌ PiCamera1 초기화 실패: {e}")
    # 레거시 환경 문제일 수 있으므로 설치 및 연결을 확인하세요.
    exit()

def encode_frame_to_base64_picam1():
    """PiCamera1을 사용하여 이미지를 캡처하고 Base64 문자열로 인코딩합니다."""
    
    # 메모리 내 바이너리 스트림 객체 생성
    stream = BytesIO()
    
    # 1. Picamera1의 capture() 메서드를 사용하여 스트림에 JPEG로 저장
    # format='jpeg'로 지정하여 인코딩을 Picamera1이 직접 처리하게 합니다.
    # quality: 1-100. (선택 사항, 기본값 85)
    try:
        # 이 한 줄이 캡처와 JPEG 인코딩을 동시에 처리합니다.
        camera.capture(stream, format='jpeg', quality=80) 
        
        # 스트림의 처음으로 포인터를 이동 (Base64 인코딩을 위해)
        stream.seek(0)
        
    except Exception as e:
        print(f"❌ Picamera1 캡처/인코딩 실패: {e}")
        return None
        
    # 2. Base64로 변환
    base64_encoded_data = base64.b64encode(stream.read()).decode('utf-8')
    stream.close() # 메모리 스트림 닫기
    return base64_encoded_data

def upload_to_firebase(base64_data):
    """Base64 데이터를 Firebase Realtime Database에 업로드합니다."""
    # 현재 시간 문자열 생성
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Firebase에 전송할 페이로드 구성
    payload = {
        "timestamp": timestamp,
        "image_base64": base64_data,
        "size_kb": len(base64_data) / 1024 # 크기 확인용
    }
    
    # Firebase REST API로 POST 요청을 보내 새 레코드를 추가합니다.
    try:
        response = requests.post(FIREBASE_URL, json=payload)
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생
        
        print(f"✅ [{timestamp}] Firebase 전송 성공. 크기: {len(base64_data) / 1024:.2f} KB")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Firebase 요청 실패: {e}")
        print("    URL 및 네트워크 설정을 확인하십시오.")
        return False

# --- 3. 메인 루프 실행 ---
if __name__ == "__main__":
    if FIREBASE_URL == "YOUR_FIREBASE_URL":
        print("\n⚠️ 경고: FIREBASE_URL을 실제 Firebase Realtime Database 주소로 변경하십시오.")
        camera.stop_preview()
        exit()
        
    try:
        while True:
            start_time = time.time()
            
            # 1. Base64 인코딩 수행
            base64_image = encode_frame_to_base64_picam1()
            
            if base64_image:
                # 2. Firebase 업로드
                upload_to_firebase(base64_image)
            
            # 3. 목표 주기(INTERVAL_SECONDS)를 맞추기 위한 대기 시간 계산
            elapsed_time = time.time() - start_time
            sleep_time = INTERVAL_SECONDS - elapsed_time
            
            if sleep_time > 0:
                # 다음 캡처까지 남은 시간만큼 대기
                print(f"    다음 캡처까지 {sleep_time:.2f}초 대기...")
                time.sleep(sleep_time)
            else:
                # 캡처 및 업로드 시간이 INTERVAL_SECONDS를 초과한 경우
                print(f"    경고: 캡처 및 업로드 시간이 {INTERVAL_SECONDS}초를 초과했습니다! 소요 시간: {elapsed_time:.2f}초")

    except KeyboardInterrupt:
        print("\n프로그램 종료.")
    finally:
        camera.stop_preview()
        print("카메라 자원 해제 완료.")
