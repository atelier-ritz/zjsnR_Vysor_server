from PyQt5 import QtCore, QtWidgets, uic
import Adafruit_GPIO as GPIO
from random import randint
from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
import threading
import atexit

# UI config
qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

mh = Adafruit_MotorHAT()

st1 = threading.Thread()
st2 = threading.Thread()
print(st1)
print(st2)
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
atexit.register(turnOffMotors)

def stepper_worker(stepper, numsteps, direction, style):
    print("{} starts steppin!".format(stepper.motornum))
    stepper.step(numsteps, direction, style)
    print("{} is done!".format(stepper.motornum))

class GUI(QtWidgets.QMainWindow,Ui_MainWindow):
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.btn_setparam.clicked.connect(self.on_btn_setparam)
        self.btn_motorgo1.clicked.connect(self.on_btn_motorgo1)
        self.btn_motorgo2.clicked.connect(self.on_btn_motorgo2)
        self.btn_touch.clicked.connect(self.on_btn_touch)

    def on_btn_setparam(self):
        mystepper1 = mh.getStepper(1)
        mystepper2 = mh.getStepper(2)
        rpm1 = self.spb_rpm1.value()
        rpm2 = self.spb_rpm2.value()
        stepperrev1 = self.spb_stepperrev1.value()
        stepperrev2 = self.spb_stepperrev2.value()
        # print(rpm1, rpm2, stepperrev1, stepperrev2)
        mystepper1.setSpeed(rpm1)
        mystepper2.setSpeed(rpm2)
        mystepper1.setStepsPerRev(stepperrev1)
        mystepper2.setStepsPerRev(stepperrev2)
    def on_btn_motorgo1(self):
##        if not st1.isAlive():
        val = self.spb_steps1.value()
        if val == 0 :
            return
        step = abs(val)
        direction = int(val/step)
        # print(step, direction)
        st1 = threading.Thread(target=stepper_worker, args=(mh.getStepper(1), step, direction, Adafruit_MotorHAT.DOUBLE,))
        st1.start()
    def on_btn_motorgo2(self):
##        if not st2.isAlive():
        val = self.spb_steps2.value()
        if val == 0 :
            return
        step = abs(val)
        direction = int(val/step)
        # print(step, direction)
        st2 = threading.Thread(target=stepper_worker, args=(mh.getStepper(2), step, direction, Adafruit_MotorHAT.DOUBLE,))
        st2.start()
    def on_btn_touch(self):
        period = spb_period
        
