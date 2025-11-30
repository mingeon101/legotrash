import firebase_admin
from firebase_admin import credentials, db
import subprocess
import time
import os


# ref = db.reference('moterSpeed')
# ref.update({"motor1": xvalue, "motor2": yvalue, "motor3": zvalue})

# Firebase Admin SDK 인증 정보
cred = credentials.Certificate("/home/user/trash/rhkdrh-firebase-adminsdk-fbsvc-53eafb3fdf.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rhkdrh-default-rtdb.firebaseio.com/'
})

# pybricksdev.exe 경로
PYBRICKSDEV_PATH = os.path.expanduser(
    r"/home/user/miniconda3/envs/gor/bin/pybricksdev"
)

# 허브 이름
HUB_NAME = "trash"

# 모터 실행 함수

def run_motor_script(m1, m2, m3, n1, n2, n3):
    with open("run_motor.py", "w",encoding='utf-8') as f:
        f.write(f"""# -*- coding: utf-8 -*-
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()
motorA = Motor(Port.A)
motorB = Motor(Port.B)
motorC = Motor(Port.F)
speed = 700

speed=300
# 기물 잡기               
motorC.run_target(speed, 0, then=Stop.HOLD, wait=True)
wait(1000)
motorC.run_target(speed, 100, then=Stop.HOLD, wait=True)
wait(10000)
motorC.run_target(speed, 0, then=Stop.HOLD, wait=True)
wait(1000)

speed=700
# 선택된 위치로 이동
motorA.run_angle(speed, {-m1},wait=False)
motorB.run_angle(speed, {m2},wait=True)
wait(1000)

speed=300
# 기물 내리기               
motorC.run_target(speed, 0, then=Stop.HOLD, wait=True)
wait(1000)
motorC.run_target(speed, 100, then=Stop.HOLD, wait=True)
wait(10000)
motorC.run_target(speed, 0, then=Stop.HOLD, wait=True)
wait(1000)

speed=700
# 이동 후 원위치 정렬
motorB.run_angle(speed, {-m2},wait=False)
motorA.run_angle(speed, {m1},wait=True)
wait(1000)

# motorB.run_angle(speed, -3900)
# wait(1000)
# motorA.run_angle(speed, -3600)
# wait(1000)
# motorB.run_angle(speed, 3900)
# wait(1000)
# motorA.run_angle(speed, 3600)
# wait(1000)

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
    speeds1 = db.reference('/moterSpeed1').get()
    if speeds1:
        n1 = speeds1.get('motor1', 0)
        n2 = speeds1.get('motor2', 0)
        n3 = speeds1.get('motor3', 0)

        print(f"motor1: {n1-m1}, motor2: {n2-m2}, motor3: {m3}")

        run_motor_script(m1, m2, m3, n1, n2, n3)
        time.sleep(7000)
    else:
        print("Firebase에서 값을 불러올 수 없습니다.")

    time.sleep(10)
