# File name:    CarSEx: car simulation experiment
# Author:       CheeseBall
# Purpose:      Pass the time

import pygame
from pygame import gfxdraw
from pygame import font
import math
font.init()

clock=pygame.time.Clock()

sw,sh=400,300

window=pygame.display.set_mode((sw,sh))

displayHP = 0
displayLbFt = 0
defaultFont = font.Font(font.get_default_font(),10)


class CarType:
  rotation: float
  steering: float
  speed: float
  accel: float
  outputSpeed: int
  gasPedal: float
  controlThrottle: float
  controlThrottle2:float
  throttle: float
  brake: float
  clutch: float
  engFriction: float
  dynamicFriction: float
  tireFriction: float
  gear: int
  gearMax: int
  gearRatios: list
  diffRatio: float
  finalGear: float

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
  currentTorqueNRpm:list

  # actively changing shiz
  rpm: int  # crankshaft rotations per minute
  rps: float # crankshaft rads per second
  w: float # power output in kilowatts (1kw = 1.341022hp)
  nm: float # torque output in newton-meters (1nm = 0.7375621493ft lbs)

  # wheels
  wheels: list


class WheelType:
  stiffness: float
  ride: float
  temp: float
  pressure: float
  angle: float # for steering n stuff
  speed: float # rpm (probably)
  radiusTyre: float
  diameterRim: float
  frict: float
  grip: float
  driven: bool


# car settings
car = CarType()
car.rotation    = 0
car.steering    = 0
car.speed       = 0
car.accel       = 0
car.gasPedal    = 0
car.controlThrottle=0
car.controlThrottle2=0
car.throttle    = 0
car.brake       = 0
car.clutch      = 0
car.engFriction = 0.99
car.dynamicFriction = 0.03
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

car.mass        = 1100
car.centerOfMassX=122
car.centerOfMassY=140
car.centerOfMassZ=40
car.deltaMass   = (0,0,0)

car.idleSpeed   = 1000
car.revLimit    = 12000

car.torqueCurve = [
  [0,0,0],
  [500,10,0],
  [1000,25,0],
  [1500,60,-20],
  [2000,100,-50],
  [2500,150,-65],
  [3000,195,-65],
  [3500,230,-65],
  [4000,250,-65],
  [4500,300,-65],
  [5000,310,-65],
  [5500,315,-65],
  [6000,300,-65],
  [6500,280,-65],
  [7000,260,-65],
  [7500,255,-65],
  [8000,230,-65],
  [8500,200,-65],
  [9000,190,-65],
  [9500,180,-65],
  [10000,170,-65],
  [10500,150,-65],
  [11000,130,-65],
  [11500,100,-65],
  [12000,90,-65],
  [12500,50,-65],
  [13000,30,-65],
  [13500,10,-65],
  [14000,0,-65],
  [14500,-10,-65]
]
car.gearRatios = [
  0.00,
  3.20,
  2.50,
  2.10,
  1.50,
  1.10,
  0.80,
  -1.00
]
car.diffRatio = 1.3
car.finalGear = 2.5

car.currentTorqueNRpm = [0,0]

car.rpm         = 1000
car.rps         = (car.rpm/9.5492965964254)/60
car.w           = 0
car.nm          = 0

car.wheels      = []

for i in range(4):
  car.wheels.append(WheelType())
for i in range(4):
  if i < 2:
    car.wheels[i].angle = 0
    car.wheels[i].speed = 0
    car.wheels[i].temp = 0
    car.wheels[i].pressure = 3
    car.wheels[i].frict = 45
    car.wheels[i].radiusTyre = 1
    car.wheels[i].diamterRim = 10
    car.wheels[i].grip = 0
    car.wheels[i].driven = False
  if i>= 2:
    car.wheels[i].angle = 0
    car.wheels[i].speed = 0
    car.wheels[i].temp = 0
    car.wheels[i].pressure = 3
    car.wheels[i].frict = 45
    car.wheels[i].grip = 0
    car.wheels[i].driven = True
# for i in range(len(car.wheels)):
#   print(car.wheels[i].__dict__)
del i

def clamp(n,smallest,largest):
  return max(smallest,min(n,largest))


def textLabel(t,x,y,c,f,a,aa,cy):
  # I know my variable naming scheme is annoying and confusing so here's a legend for this
  # vvv   legend         vvv
  # t:    (string)       text
  # x:    (int/float)    position X
  # y:    (int/float)    position Y
  # s:    (int/float)    text size
  # c:    (tuple)        text colour
  # f:    (font)         font
  # a:    (int)          alignment (1 for left align, 2 for center align, 3 for right align)
  # aa:   (bool)         anti aliasing
  # cy:   (bool)         center y or not
  # vvv   function       vvv
  # this was writen at about the time that I changed my formatting to be more compact and similar to what I'm used to
  # see? I'm capable of writing readable code, I just don't want to.
  if type(t)!=str():
    t=str(t)
  l=f.render(t,aa,c)
  tr=l.get_rect()
  if a==1:
    tr.left=x
  if a==2:
    tr.centerx=x
  if a==3:
    tr.right=x
  if cy: tr.centery = y
  else: tr.y = y
  tp = tr
  window.blit(l,tp)


def curve():
  for i in range(len(car.torqueCurve)):
    if i < len(car.torqueCurve):
      if car.torqueCurve[i][0] <= car.rpm < car.torqueCurve[i+1][0]:
        # maximum torque curve
        x1,x2 = (car.torqueCurve[i][0]/9.5492965964254)/60,(car.torqueCurve[i+1][0]/9.5492965964254)/60 # rpm
        y1,y2 = car.torqueCurve[i][1],car.torqueCurve[i+1][1] # torque
        x=car.rps
        y=y1+(x-x1)*((y2-y1)/(x2-x1))
        car.currentTorqueNRpm[0]=y
        # minimum torque curve
        x1,x2 = (car.torqueCurve[i][0]/9.5492965964254)/60,(car.torqueCurve[i+1][0]/9.5492965964254)/60 # rpm
        y1,y2 = car.torqueCurve[i][2],car.torqueCurve[i+1][2] # torque
        x=car.rps
        y=y1+(x-x1)*((y2-y1)/(x2-x1))
        car.currentTorqueNRpm[1]=y


def engineSim():
  # 1 - tanh( (4 * ( ( car.rpm - car.idleSpeed) / car.idleSpeed+100 ) ) ) - car.controlThrottle
  car.controlThrottle = (1 - math.tanh( (4 * ( ( car.rpm - car.idleSpeed) / (car.idleSpeed+100) ) ) ) )
  car.controlThrottle = clamp(car.controlThrottle,0,1)
  car.throttle = max(car.gasPedal,car.controlThrottle)
  car.controlThrottle2 = (1 - math.tanh( (4 * ( ( car.rpm - car.revLimit) / (car.revLimit-100) ) ) ) )
  car.controlThrottle2 = clamp(car.controlThrottle2,0,1)
  car.throttle = min(car.throttle,car.controlThrottle2)
  # inertia: (Mass*Length^2)/3
  # inertia = (2*(3*3))/3
  # rotational acceleration: nm/inertia
  car.nm = linearInterp(car.currentTorqueNRpm[0],car.currentTorqueNRpm[1],car.throttle)
  car.w = car.nm * car.rps

  totalRatio = car.gearRatios[car.gear] * car.finalGear * car.diffRatio
  engineInt = max((car.wheels[2].speed+car.wheels[3].speed)/2*totalRatio,car.idleSpeed)

  if car.throttle != 0 or car.clutch <= 0.5:
    car.rps = min(engineInt,car.revLimit/9.5492965964254/60)
  else:
    car.rps = (car.revLimit/9.5492965964254/60 - (1-car.throttle) * (car.revLimit/9.5492965964254/60 - car.idleSpeed/9.5492965964254/60))

  if car.clutch <= 0.5:
    car.nm = (1-car.clutch)*car.throttle * (car.currentTorqueNRpm[0]-car.currentTorqueNRpm[1])+car.currentTorqueNRpm[0]
  else: car.nm = 0

  if car.speed <= 0: car.nm = max(0,car.nm)
  else: car.nm = car.nm

  car.rpm = car.rps * (1/2*math.pi) * 60

  # print(car.rpm)
  # Power (W) = Torque (N.m) ∙ Speed (rpm) / 9.5488
  car.outputSpeed = (car.nm / car.mass) * (car.diffRatio * car.gearRatios[car.gear])
  for i in range(len(car.wheels)):
    if car.wheels[i].driven:
      car.wheels[i].speed = ((car.nm*0.99*car.gearRatios[car.gear])/2)*(-(math.tanh(car.rps-car.revLimit)+1)/2)
  car.speed += car.accel
  # print(car.accel)
  HP = car.w / 745.7
  LbFt = car.nm * 0.7375621493
  return HP,LbFt
  # print(car.nm)


def tireSim():
  pass


def linearInterp(a,b,t):
  return a*t + b*(-t+1)


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
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_UP and car.gear<6:
        oldGear = car.gear
        car.gear+=1
      if event.key == pygame.K_DOWN and car.gear>-1:
        oldGear=car.gear
        car.gear-=1

  if allKeys[pygame.K_w]: car.gasPedal += 0.1
  else: car.gasPedal -= 0.1
  if allKeys[pygame.K_s]: car.brake += 0.2
  else: car.brake -= 0.2
  if allKeys[pygame.K_c]: car.clutch += 0.50
  else: car.clutch -= 0.50
  car.gasPedal = clamp(car.gasPedal,0,1)
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
  pygame.gfxdraw.line(window,50,50,int(50-car.accel*-15),int(50),(0,255,0))
  pygame.gfxdraw.line(window,50,40,int(50-car.speed*-1),int(40),(0,255,255))
  pygame.draw.rect(window,(0,255,0),(110,5,20,car.gasPedal*90),1)
  pygame.gfxdraw.rectangle(window,(sw//2-100,275,200,45),(255,255,255))
  pygame.gfxdraw.rectangle(window,(sw//2-3+car.steering*1000,275,6,45),(255,0,0))
  pygame.gfxdraw.rectangle(window,(270,5,20,int(car.rpm/100)),(255,255,255))
  pygame.gfxdraw.rectangle(window,(15+car.gear*10,275,5,20),(255,255,255))
  for i in range(len(car.wheels)):
    if car.wheels[i].driven:
      pygame.gfxdraw.rectangle(window,(300+i*15,150,10,15*car.wheels[i].speed),(0,255,0))
    else:
      pygame.gfxdraw.rectangle(window,(300+(i+2)*15,120,10,15),(255,255,255))
  textLabel(f"throttle:{round(car.throttle,2),round(car.controlThrottle2*100)/100}f",10,210,(255,255,255),defaultFont,1,True,False)
  textLabel((f"power: {displayHP}hp"),10,250,(255,255,255),defaultFont,1,True,False)
  textLabel((f"outputSpeed: {car.outputSpeed}rpm"),10,240,(255,255,255),defaultFont,1,True,False)
  textLabel((f"speed: {round(car.speed*60,2)}km/h"),10,230,(255,255,255),defaultFont,1,True,False)
  textLabel((f"rpm: {round(car.rpm)}rpm"),10,220,(255,255,255),defaultFont,1,True,False)
  textLabel((f"nm: {round(car.nm,2)}nm"),10,200,(255,255,255),defaultFont,1,True,False)
  # todo draw car and movement vector + acceleration/deceleration


while True:
  window.fill((15,15,15))
  getInput()
  curve()
  moveCar()
  displayHP,displayLbFt = engineSim()
  drawCar()
  weightTransfer()
  pygame.display.update()
  pygame.event.clear()
  clock.tick(30)
