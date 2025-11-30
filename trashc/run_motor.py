# -*- coding: utf-8 -*-
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
motorA.run_angle(speed, -1000,wait=False)
motorB.run_angle(speed, 1000,wait=True)
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
motorB.run_angle(speed, -1000,wait=False)
motorA.run_angle(speed, 1000,wait=True)
wait(1000)

# motorB.run_angle(speed, -3900)
# wait(1000)
# motorA.run_angle(speed, -3600)
# wait(1000)
# motorB.run_angle(speed, 3900)
# wait(1000)
# motorA.run_angle(speed, 3600)
# wait(1000)

