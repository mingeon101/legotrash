import requests
import base64
import numpy as np
import cv2
import time
import os

# --- 1. 설정 변수 ---
FIREBASE_URL_BASE = "https://rhkdrh-default-rtdb.firebaseio.com/camera_data" 
POLLING_INTERVAL = 0.5 # 데이터베이스를 확인할 간격 (초)
OUTPUT_FILENAME = "output.png" # 저장할 이미지 파일 이름
DISPLAY_DURATION = 100 # 새 이미지를 화면에 표시할 시간 (밀리초)

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
    delete_url = f"{FIREBASE_URL_BASE}/{key}.json"
    
    try:
        response = requests.delete(delete_url)
        response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
        
        print(f"   ✅ 데이터베이스 삭제 성공: 키 {key}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 데이터베이스 삭제 실패 (키: {key}): {e}")
        return False

def monitor_firebase_save_and_delete():
    """Firebase를 주기적으로 확인하고, 가장 오래된 이미지를 처리(저장 및 표시)한 후 삭제합니다."""
    
    print("✅ Firebase 감지, PNG 저장 및 데이터베이스 삭제 시작.")
    print(f"   최신 이미지는 '{OUTPUT_FILENAME}'으로 덮어쓰기 되며, 처리된 데이터는 즉시 삭제됩니다.")
    print("   'q'를 누르거나 터미널에서 Ctrl+C를 눌러 종료하세요.")
    
    while True:
        start_time = time.time()
        
        try:
            # 1. Firebase 데이터 요청
            fetch_url = f"{FIREBASE_URL_BASE}.json"
            response = requests.get(fetch_url)
            response.raise_for_status() 
            all_data = response.json()

            if all_data:
                # 2. 키를 시간순으로 정렬하여 가장 '오래된' 키부터 처리합니다.
                # 이는 큐(Queue)처럼 작동하여 처리 누락을 방지합니다.
                sorted_keys = sorted(all_data.keys())
                
                # '가장 오래된' 데이터 하나만 처리
                key_to_process = sorted_keys[0] 
                record = all_data[key_to_process]
                
                base64_data = record.get('image_base64')
                timestamp = record.get('timestamp', 'Unknown Time')

                if base64_data:
                    img = decode_base64_to_image(base64_data)
                    
                    if img is not None:
                        # 3. 화면 표시를 위한 텍스트 추가
                        cv2.putText(img, 
                                    f"Time: {timestamp}", 
                                    (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                                    (0, 255, 255), 2)
                        
                        # 4. PNG 파일로 저장 (덮어쓰기)
                        cv2.imwrite(OUTPUT_FILENAME, img)
                        print(f"🎉 이미지 저장 완료 (시간: {timestamp}). 파일: {OUTPUT_FILENAME}")
                        
                        # 5. 화면에 표시 (짧은 시간만)
                        cv2.imshow("Live Firebase Image (Press 'q' to quit)", img)
                        
                        if cv2.waitKey(DISPLAY_DURATION) & 0xFF == ord('q'):
                            raise KeyboardInterrupt
                            
                        # 6. 저장 및 표시 완료 후, 데이터베이스에서 삭제
                        delete_from_firebase(key_to_process)
                        
                    else:
                        print(f"경고: 키 {key_to_process} 이미지 디코딩 실패. 데이터 삭제 시도.")
                        delete_from_firebase(key_to_process)
                else:
                    print(f"경고: 키 {key_to_process} 데이터에 이미지가 없습니다. 데이터 삭제 시도.")
                    delete_from_firebase(key_to_process)
            else:
                # 데이터베이스가 비어있는 경우
                print("데이터베이스에 처리할 새 이미지가 없습니다.")


        except requests.exceptions.RequestException as e:
            print(f"❌ Firebase 연결 오류: {e}. 권한 및 URL 확인.")
        except KeyboardInterrupt:
            # Ctrl+C 또는 'q' 키 입력으로 종료
            break

        # 7. 다음 폴링까지 대기
        elapsed_time = time.time() - start_time
        sleep_time = max(0, POLLING_INTERVAL - elapsed_time)
        time.sleep(sleep_time)


    # 8. 종료 시 자원 해제
    cv2.destroyAllWindows()
    print("프로그램 종료.")

# --- 메인 실행 ---
if __name__ == "__main__":
    monitor_firebase_save_and_delete()
