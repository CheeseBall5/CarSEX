# File name:    CarSEx: car simulation experiment
# Author:       CheeseBall
# Purpose:      Pass the time

import pygame
from pygame import gfxdraw
import math

clock=pygame.time.Clock()

sw,sh=400,300

window=pygame.display.set_mode((sw,sh))

displayHP = 0
displayLbFt = 0


class CarType:
  rotation: float
  steering: float
  speed: pygame.math.Vector2()
  accel: pygame.math.Vector2()
  gas: float
  brake: float
  clutch: float
  engFriction: float
  tireFriction: float
  gear: int
  gearMax: int

  # sus
  frontStiffness: int
  frontDampening: int
  frontRide: int
  rearStiffness: int
  rearDampening: int
  rearRide: int
  frontWidth:int
  rearWidth:int

  # center of mass (0 being the back/left/bottom and 255 being the front/right/top) (imagine square car lmfao)
  centerOfMassY: int
  centerOfMassX: int
  centerOfMassZ: int # up, not left/right
  deltaMass    : tuple

  # car setting shiz below
  mass: int # kilograms (maybe)
  idleSpeed: int
  revLimit: int

  torqueCurve: list
  currentTorqueNRpm:tuple

  # actively changing shiz
  rpm: int  # crankshaft rotations per minute
  w: float # power output in kilowatts (1kw = 1.341022hp)
  nm: float # torque output in newton-meters (1nm = 0.7375621493ft lbs)

  # wheels
  wheels: list


class WheelType:
  stiffness: float
  ride: float

  angle: float # for steering n stuff
  speed: float # rpm (probably)
  frict: float
  grip: float
  driven: bool


# car settings
car = CarType()
car.rotation    = 0
car.steering    = 0
car.speed       = pygame.math.Vector2(0,0)
car.accel       = pygame.math.Vector2(0,0)
car.gas         = 0
car.brake       = 0
car.clutch      = 0
car.engFriction = 0.2
car.tireFriction= 0.2
car.gear        = 0
car.gearMax     = 6

car.frontWidth   = 60
car.rearWidth    = 65
car.frontDampening=130
car.frontStiffness=130
car.frontRide    = 100
car.rearDampening= 130
car.rearStiffness= 130
car.rearRide     = 100

car.mass        = 2500
car.centerOfMassX=122
car.centerOfMassY=140
car.centerOfMassZ=40
car.deltaMass   = (0,0,0)

car.idleSpeed   = 1000
car.revLimit    = 8500

car.torqueCurve = [
  [0,0],
  [500,10],
  [1000,25],
  [1500,60],
  [2000,100],
  [2500,150],
  [3000,195],
  [3500,240],
  [4000,250],
  [4500,220],
  [5000,180],
  [5500,110],
  [6000,100],
  [6500,95],
  [7000,92],
  [7500,90],
  [8000,85],
  [8500,50],
]
car.currentTorqueNRpm = (0,0)

car.rpm         = 0
car.w           = 0
car.nm          = 0

car.wheels      = []

for i in range(4):
  car.wheels.append(WheelType())
for i in range(4):
  if i < 2:
    car.wheels[i].angle = 0
    car.wheels[i].speed = 0
    car.wheels[i].frict = 45
    car.wheels[i].grip = 0
    car.wheels[i].driven = False
  if i>= 2:
    car.wheels[i].angle = 0
    car.wheels[i].speed = 0
    car.wheels[i].frict = 45
    car.wheels[i].grip = 0
    car.wheels[i].driven = True
# for i in range(len(car.wheels)):
#   print(car.wheels[i].__dict__)

def clamp(n,smallest,largest):
  return max(smallest,min(n,largest))


def curve():
  for i1 in range(len(car.torqueCurve)):
    if i1 < len(car.torqueCurve):
      if car.torqueCurve[i1][0] <= car.rpm < car.torqueCurve[i1+1][0]:
        x1,x2 = car.torqueCurve[i1][0],car.torqueCurve[i1+1][0]# rpm
        y1,y2 = car.torqueCurve[i1][1],car.torqueCurve[i1+1][1] # torque
        x=(car.torqueCurve[i1][0]/car.torqueCurve[i1+1][0])*(500*i1)
        print("x: ",x)
        y=y1+(x-x1)*((y2-y1)/(x2-x1))
        car.currentTorqueNRpm=(y)
        print("current torque: ",car.currentTorqueNRpm)


def engineSim():
  car.nm = car.currentTorqueNRpm
  car.w = car.nm * car.rpm / 9.5488
  car.rpm = clamp(car.rpm,car.idleSpeed,car.revLimit)
  car.rpm += (car.gas*car.nm-car.engFriction) * 10
  # print(car.rpm)
  # Power (W) = Torque (N.m) ∙ Speed (rpm) / 9.5488
  car.accel = (car.nm / car.mass) * pygame.time.get_ticks()
  # print(car.accel)
  displayHP = car.w/745.7
  displayLbFt = car.nm * 0.7375621493
  # print(car.nm)


def tireSim():
  pass


def getInput():
  allKeys=pygame.key.get_pressed()

  if allKeys[pygame.K_a]:
    car.steering-=0.01
  if allKeys[pygame.K_d]:
    car.steering+=0.01
  if not allKeys[pygame.K_a] and not allKeys[pygame.K_d]:
    if -0.02 < car.steering < 0.2: car.steering = 0
    elif car.steering > 0.01: car.steering -= 0.01
    elif car.steering < 0.01: car.steering += 0.01
  car.steering = clamp(car.steering,-0.1,0.1)
  if allKeys[pygame.K_UP] and car.gear<6:
    car.gear+=1
  if allKeys[pygame.K_DOWN] and car.gear>-1:
    car.gear-=1

  if allKeys[pygame.K_w]: car.gas += 0.05
  else: car.gas -= 0.05
  if allKeys[pygame.K_s]: car.brake += 0.2
  else: car.brake -= 0.2
  if allKeys[pygame.K_c]: car.clutch += 0.45
  else: car.clutch -= 0.45
  car.gas = clamp(car.gas,0,1)
  car.brake = clamp(car.brake,0,1)
  car.clutch = clamp(car.clutch,0,1)


def weightTransfer():
  car.deltaMass = car.accel * (car.centerOfMassZ/car.frontWidth) * car.mass
  # print(car.deltaMass)


def moveCar():
  pass
  # print(car.accel, car.speed)


def drawCar():
  pygame.gfxdraw.aacircle(window,50,50,45,(255,255,255))
  pygame.gfxdraw.filled_circle(window,50,50,2,(0,0,255))
  pygame.gfxdraw.line(window,50,50,int(50-car.accel.x*15),int(50-car.accel.y*15),(0,255,0))
  pygame.gfxdraw.line(window,50,50,int(50-car.speed.x*10),int(50-car.speed.y*10),(0,255,255))
  pygame.draw.rect(window,(0,255,0),(110,5,20,car.gas*90),1)
  pygame.gfxdraw.rectangle(window,(sw//2-100,275,200,45),(255,255,255))
  pygame.gfxdraw.rectangle(window,(sw//2-3+car.steering*1000,275,6,45),(255,0,0))
  # todo draw car and movement vector + acceleration/deceleration


while True:
  window.fill((15,15,15))
  getInput()
  curve()
  # moveCar()
  # drawCar()
  engineSim()
  weightTransfer()
  pygame.display.update()
  pygame.event.clear()
  clock.tick(30)
