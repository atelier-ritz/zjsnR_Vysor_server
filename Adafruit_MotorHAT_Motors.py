import time
from Adafruit_PWM_Servo_Driver import PWM

class Adafruit_StepperMotor:
    MICROSTEPS = 8
    MICROSTEP_CURVE = [0, 50, 98, 142, 180, 212, 236, 250, 255]

    def __init__(self, controller, num, steps=100):
        self.MC = controller
        self.revsteps = steps
        self.motornum = num
        self.sec_per_step = 0.03
        self.steppingcounter = 0
        self.currentstep = 0

        num -= 1

        if (num == 0):
            self.PWMA = 8
            self.AIN2 = 9
            self.AIN1 = 10
            self.PWMB = 13
            self.BIN2 = 12
            self.BIN1 = 11
        elif (num == 1):
            self.PWMA = 2
            self.AIN2 = 3
            self.AIN1 = 4
            self.PWMB = 7
            self.BIN2 = 6
            self.BIN1 = 5
        else:
            raise NameError('MotorHAT Stepper must be between 1 and 2 inclusive')

    def setSpeed(self, rpm):
        self.sec_per_step = 60.0 / (self.revsteps * rpm)
        self.steppingcounter = 0

    def setStepsPerRev(self,val):
        self.revsteps = val

    def oneStep(self, dir, style):
        pwm_a = pwm_b = 255

        # first determine what sort of stepping procedure we're up to
        if (style == Adafruit_MotorHAT.SINGLE):
            if ((self.currentstep//(self.MICROSTEPS//2)) % 2):
                # we're at an odd step, weird
                if (dir == Adafruit_MotorHAT.FORWARD):
                    self.currentstep += self.MICROSTEPS//2
                else:
                    self.currentstep -= self.MICROSTEPS//2
            else:
                # go to next even step
                if (dir == Adafruit_MotorHAT.FORWARD):
                    self.currentstep += self.MICROSTEPS
                else:
                    self.currentstep -= self.MICROSTEPS
        if (style == Adafruit_MotorHAT.DOUBLE):
            if not (self.currentstep//(self.MICROSTEPS//2) % 2):
                # we're at an even step, weird
                if (dir == Adafruit_MotorHAT.FORWARD):
                    self.currentstep += self.MICROSTEPS//2
                else:
                    self.currentstep -= self.MICROSTEPS//2
            else:
                # go to next odd step
                if (dir == Adafruit_MotorHAT.FORWARD):
                    self.currentstep += self.MICROSTEPS
                else:
                    self.currentstep -= self.MICROSTEPS
        if (style == Adafruit_MotorHAT.INTERLEAVE):
            if (dir == Adafruit_MotorHAT.FORWARD):
                self.currentstep += self.MICROSTEPS//2
            else:
                self.currentstep -= self.MICROSTEPS//2

        # go to next 'step' and wrap around
        self.currentstep += self.MICROSTEPS * 4
        self.currentstep %= self.MICROSTEPS * 4

        # only really used for microstepping, otherwise always on!
        self.MC._pwm.setPWM(self.PWMA, 0, pwm_a*16)
        self.MC._pwm.setPWM(self.PWMB, 0, pwm_b*16)

        # set up coil energizing!
        coils = [0, 0, 0, 0]

        step2coils = [     [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1] ]
        coils = step2coils[self.currentstep//(self.MICROSTEPS//2)]

        #print "coils state = " + str(coils)
        self.MC.setPin(self.AIN2, coils[0])
        self.MC.setPin(self.BIN1, coils[1])
        self.MC.setPin(self.AIN1, coils[2])
        self.MC.setPin(self.BIN2, coils[3])

        return self.currentstep

    def step(self, steps, direction, stepstyle):
        s_per_s = self.sec_per_step
        lateststep = 0
        if (stepstyle == Adafruit_MotorHAT.INTERLEAVE):
            s_per_s = s_per_s / 2.0
        print("{} sec per step".format(s_per_s))

        for s in range(steps):
            time_before_start = time.time()
            lateststep = self.oneStep(direction, stepstyle)
            # time.sleep(s_per_s)
            towait = time.time() - time_before_start - s_per_s
            if towait > 0:
                time.sleep(towait)
            else:
                continue


class Adafruit_MotorHAT:
    FORWARD = 1
    BACKWARD = 2
    BRAKE = 3
    RELEASE = 4

    SINGLE = 1
    DOUBLE = 2
    INTERLEAVE = 3
    MICROSTEP = 4

    def __init__(self, addr = 0x60, freq = 1600, i2c=None, i2c_bus=None):
        self._frequency = freq
        self.steppers = [ Adafruit_StepperMotor(self, 1), Adafruit_StepperMotor(self, 2) ]
        self._pwm = PWM(addr, debug=False, i2c=i2c, i2c_bus=i2c_bus)
        self._pwm.setPWMFreq(self._frequency)

    def setPin(self, pin, value):
        if (pin < 0) or (pin > 15):
            raise NameError('PWM pin must be between 0 and 15 inclusive')
        if (value != 0) and (value != 1):
            raise NameError('Pin value must be 0 or 1!')
        if (value == 0):
            self._pwm.setPWM(pin, 0, 4096)
        if (value == 1):
            self._pwm.setPWM(pin, 4096, 0)

    def getStepper(self, num):
        if (num < 1) or (num > 2):
            raise NameError('MotorHAT Stepper must be between 1 and 2 inclusive')
        return self.steppers[num-1]
