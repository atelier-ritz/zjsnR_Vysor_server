from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
from server import Server
import threading
import atexit
import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21,GPIO.OUT)

mh = Adafruit_MotorHAT()

def turnOffMotors():
    mh.getStepper(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getStepper(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getStepper(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getStepper(4).run(Adafruit_MotorHAT.RELEASE)
    GPIO.cleanup()
atexit.register(turnOffMotors)

def stepper_worker(stepper, numsteps, direction, style):
    print("Motor {} starts stepping!".format(stepper.motornum))
    stepper.step(numsteps, direction, style)
    print("Motor {} is done!".format(stepper.motornum))
    svr.client[0][0].sendto('Motor {} is done!'.format(stepper.motornum).encode(), svr.client[0][1])

def analyzecmd(cmd):
    print('Command - {}'.format(cmd))
    if cmd[0] == 'setparam':
        mystepper1 = mh.getStepper(1)
        mystepper2 = mh.getStepper(2)
        mystepper1.setStepsPerRev(int(cmd[3]))
        mystepper2.setStepsPerRev(int(cmd[4]))
        mystepper1.setSpeed(int(cmd[1]))
        mystepper2.setSpeed(int(cmd[2]))
    if cmd[0] == 'motorgo1':
        th1 = threading.Thread(target=stepper_worker,
                                args=(mh.getStepper(2), int(cmd[1]), int(cmd[2]),
                                Adafruit_MotorHAT.DOUBLE,))
        th1.start()
    if cmd[0] == 'motorgo2':
        th2 = threading.Thread(target=stepper_worker,
                                args=(mh.getStepper(1), int(cmd[1]), int(cmd[2]),
                                Adafruit_MotorHAT.DOUBLE,))
        th2.start()
    if cmd[0] == 'touch':
        GPIO.output(21,True)
        time.sleep(float(cmd[1]))
        GPIO.output(21,False)

if __name__ == "__main__":
    svr = Server()
    svr.start()
    while True:
        command = svr.getcmd()
        if command == 'quit':
            break
        if not command == ['']:
            analyzecmd(command)
            svr.clccmd()
        time.sleep(.05)
    sys.exit()
