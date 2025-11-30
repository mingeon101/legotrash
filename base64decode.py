import requests
import base64
import numpy as np
import cv2
import time

# --- 1. 설정 변수 ---
# 데이터베이스의 기본 경로 (키를 뒤에 추가하여 사용)
FIREBASE_URL_BASE = "https://rhkdrh-default-rtdb.firebaseio.com/camera_data" 
POLLING_INTERVAL = 0.01 # 데이터베이스를 확인할 간격 (초)
DISPLAY_DURATION = 10 # 새 이미지를 화면에 표시할 시간 (밀리초, 500ms = 0.5초)

def decode_base64_to_image(base64_data):
    """Base64 문자열을 OpenCV 이미지 객체로 변환합니다."""
    try:
        image_bytes = base64.b64decode(base64_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img_decoded
    except Exception as e:
        # print(f"❌ 이미지 디코딩 중 오류 발생: {e}")
        return None

def delete_from_firebase(key):
    """지정된 키의 데이터를 Firebase에서 삭제합니다."""
    
    # 삭제할 노드의 전체 URL: BASE_URL/key.json
    delete_url = f"{FIREBASE_URL_BASE}/{key}.json"
    
    try:
        response = requests.delete(delete_url)
        response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
        
        print(f"   ✅ 삭제 성공: 키 {key}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 삭제 실패 (키: {key}): {e}")
        return False

def monitor_firebase():
    """Firebase를 주기적으로 확인하고 새 이미지를 표시한 후 삭제합니다."""
    
    print("✅ Firebase 자동 감지 및 삭제 시작.")
    print("   'q'를 누르거나 터미널에서 Ctrl+C를 눌러 종료하세요.")
    
    while True:
        start_time = time.time()
        
        try:
            # 1. Firebase 데이터 요청 (BASE_URL.json으로 모든 데이터를 가져옴)
            fetch_url = f"{FIREBASE_URL_BASE}.json"
            response = requests.get(fetch_url)
            response.raise_for_status() 
            all_data = response.json()

            if all_data:
                # 2. 키를 시간순으로 정렬하여 처리 (가장 오래된 것부터 처리)
                sorted_keys = sorted(all_data.keys())
                
                for key in sorted_keys:
                    record = all_data[key]
                    base64_data = record.get('image_base64')
                    timestamp = record.get('timestamp', 'Unknown Time')

                    if base64_data:
                        img = decode_base64_to_image(base64_data)
                        
                        if img is not None:
                            # 3. 화면에 표시
                            cv2.putText(img, 
                                        f"Time: {timestamp}", 
                                        (10, 30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                                        (0, 255, 255), 2)
                            
                            cv2.imshow("Live Firebase Image Stream", img)
                            print(f"➡️ 이미지 표시 중 (시간: {timestamp})")
                            
                            # 4. 잠시 대기 (자동 넘김)
                            if cv2.waitKey(DISPLAY_DURATION) & 0xFF == ord('q'):
                                raise KeyboardInterrupt
                            
                            # 5. 표시 완료 후 데이터 삭제
                            delete_from_firebase(key)
                            
                        else:
                            # 디코딩 실패 시에도 삭제하여 잘못된 데이터가 쌓이는 것을 방지
                            print(f"경고: 키 {key} 이미지 디코딩 실패. 데이터 삭제 시도.")
                            delete_from_firebase(key)
                
            else:
                # 데이터베이스가 비어있는 경우
                print("데이터베이스에 새 이미지가 없습니다.")


        except requests.exceptions.RequestException as e:
            print(f"❌ Firebase 연결 오류: {e}. 권한 및 URL 확인.")
        except KeyboardInterrupt:
            # Ctrl+C 또는 'q' 키 입력으로 종료
            break

        # 6. 다음 폴링까지 대기
        elapsed_time = time.time() - start_time
        sleep_time = max(0, POLLING_INTERVAL - elapsed_time)
        print(f"   다음 확인까지 {sleep_time:.2f}초 대기...")
        time.sleep(sleep_time)


    # 7. 종료 시 자원 해제
    cv2.destroyAllWindows()
    print("프로그램 종료.")

# --- 메인 실행 ---
if __name__ == "__main__":
    monitor_firebase()
