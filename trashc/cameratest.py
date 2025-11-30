from picamera2 import Picamera2
import time
import sys

picam2 = Picamera2()

try:
    print("Ctrl+C finish the program.")
    picam2.start_preview()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Ctrl+C ")
    
except Exception as e:
    print(f"\n: {e}")
    sys.exit(1)
    
finally:
    if picam2.started:
        picam2.stop_preview()
        picam2.close()
        print(".")