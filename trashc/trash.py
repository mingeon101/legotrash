import firebase_admin
from firebase_admin import credentials, db
import subprocess
import time
import os


# ref = db.reference('moterSpeed')
# ref.update({"motor1": xvalue, "motor2": yvalue, "motor3": zvalue})

# Firebase Admin SDK 인증 정보
cred = credentials.Certificate(r"C:\Users\user\trash\rhkdrh-firebase-adminsdk-fbsvc-f0aa4766bc.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rhkdrh-default-rtdb.firebaseio.com/'
})

# pybricksdev.exe 경로
PYBRICKSDEV_PATH = os.path.expanduser(
    r"C:\Users\user\anaconda3\envs\gor\Scripts\pybricksdev.exe"
)

# 허브 이름
HUB_NAME = "trash"

# 경적 실행 함수
def run_buzzer_script(p):
    # Access 'p' to avoid unused parameter warning
    _ = p
    with open("buzzer.py", "w",encoding='utf-8') as f:
        f.write(f"""# -*- coding: utf-8 -*-
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop  
from pybricks.robotics import DriveBase
from pybricks.tools import wait
hub = PrimeHub()
# 사람이 감지되면 경적 소리 재생
if(p==1):
    # 높은 주파수의 경적 톤을 빠르게 반복
    for _ in range(3):
        # 800 Hz (비교적 높은 톤)를 200ms 동안 재생
        hub.speaker.beep(800, 200)
        # 짧은 대기 (경적 간격)
        wait(100)
""")
    try:
        subprocess.run([
            PYBRICKSDEV_PATH,
            "run", "ble",
            "--name", HUB_NAME,
            "buzzer.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[실행 오류] {e}")

# 모터 실행 함수

def run_motor_script(m1, m2, m3, p):
    # Access 'p' to avoid unused parameter warning
    _ = p
    with open("run_motor.py", "w",encoding='utf-8') as f:
        f.write(f"""# -*- coding: utf-8 -*-
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
motorA = Motor(Port.A)
motorB = Motor(Port.B)
motorC = Motor(Port.F)
speed = 700

speed=300
# 사람이 감지되지 않으면 모터 작동   
if(p==0):
    motorB.run_angle(speed, {m1},wait=False)
    motorA.run_angle(speed, {-m2},wait=False)
    if({m3} !=0):
        motorC.run_target(300, {m3},wait=True)
        motorC.run_target(-300, {m3},wait=True)
else:
    motorB.run_angle(speed, 0,wait=False)
    motorA.run_angle(speed, 0,wait=True)
""")
    try:
        subprocess.run([
            PYBRICKSDEV_PATH,
            "run", "ble",
            "--name", HUB_NAME,
            "run_motor.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[실행 오류] {e}")

# 루프 실행
while True:
    speeds = db.reference('/moterSpeed').get()
    if speeds:
        m1 = speeds.get('motor1', 0)
        m2 = speeds.get('motor2', 0)
        m3 = speeds.get('motor3', 0)
    speeds1 = db.reference('/people').get()
    if speeds1:
        p = speeds1.get('people', 0)
        print(f"motor1: {m1}, motor2: {m2}, motor3: {m3}, people: {p}")
        run_motor_script(m1, m2, m3, p)
        run_buzzer_script(p)
    else:
        print("Firebase에서 값을 불러올 수 없습니다.")
