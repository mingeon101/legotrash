from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

speed = 100
speed1 = 300
speed2 = 200
hub = PrimeHub()

motorA = Motor(Port.A) # motor right
motorB = Motor(Port.B) # motor left
motorC = Motor(Port.F) # auto door

motorC.run_target(speed, 0, then=Stop.HOLD, wait=True)
wait(1000)
motorC.run_target(speed, 100, then=Stop.HOLD, wait=True)
wait(10000)
motorC.run_target(speed, 0, then=Stop.HOLD, wait=True)
wait(1000)

motorA.run_angle(speed1,6000,wait=False)
motorB.run_angle(speed1,-6000,wait=False)
wait(3000)
motorA.run_angle(speed1,-6000,wait=False)
motorB.run_angle(speed1,6000,wait=False)
wait(3000)

motorA.run_angle(speed2,-6000,wait=False)
motorB.run_angle(speed2,-6000,wait=False)
wait(5000)
motorA.run_angle(speed2,6000,wait=False)
motorB.run_angle(speed2,6000,wait=False)
wait(5000)

motorA.run_angle(speed2,-6000,wait=False)
motorB.run_angle(speed2,-6000,wait=False)
wait(5000)

motorA.run_angle(speed1,-6000,wait=False)
motorB.run_angle(speed1,6000,wait=False)
wait(2000)

# while True:
#     motorA.run_angle(speed,50,wait=False)
#     motorB.run_angle(speed,-50,wait=False)
#     wait(1000)
#     motorA.run_angle(speed,-50,wait=False)
#     motorB.run_angle(speed,50,wait=False)
#     wait(1000)
