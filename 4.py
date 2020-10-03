'''
-------------------------------------------------------
Name: Milestone 4 - Balancing
Creator:  Group 15
Date:   04/03/2020
-------------------------------------------------------
Simple dance with stabilizer

Dance routine
-------------------------------------------------------
'''
import pyb
#from random import randint
#import random
from pyb import Pin, Timer, ADC, DAC, LED, ExtInt
import time
from array import array
from mpu6050 import MPU6050
from oled_938 import OLED_938	# Use OLED display driver
import micropython

micropython.alloc_emergency_exception_buf(100)

# Setup OLED display
oled = OLED_938(pinout={'sda': 'Y10', 'scl': 'Y9', 'res': 'Y8'}, height=64,
                   external_vcc=False, i2c_devid=61)
oled.poweron()
oled.init_display()
oled.draw_text(0,0, 'Group 15')
oled.draw_text(0, 10, 'Milestone 4: Balancing')
oled.draw_text(0, 20, 'Press USR button')
oled.display()
print('Performing Milestone 3')
print('Waiting for button press')

trigger = pyb.Switch()		# Create trigger switch object
while not trigger():		# Wait for trigger press
	time.sleep(0.001)
while trigger():
	pass			# Wait for release
print('Button pressed - Running')

oled.draw_text(0, 30, 'Button pressed - Running')
oled.display()

# Setting up 5k potentiometer
pot = pyb.ADC(Pin('X11'))
imu = MPU6050(1, False)

A1 = Pin('X3',Pin.OUT_PP)	# A is right motor
A2 = Pin('X4',Pin.OUT_PP)
B1 = Pin('X7',Pin.OUT_PP)	# B is left motor
B2 = Pin('X8',Pin.OUT_PP)
PWMA = Pin('X1')
PWMB = Pin('X2')

tim = Timer(2, freq = 10000)
motorA = tim.channel(1, Timer.PWM, pin = PWMA)
motorB = tim.channel(2, Timer.PWM, pin = PWMB)

def A_forward(value):
	A1.high()
	A2.low()
	motorA.pulse_width_percent(value)
def A_back(value):
	A1.low()
	A2.high()
	motorA.pulse_width_percent(value)
def A_stop():
	A1.low()
	A2.low()
	motorA.pulse_width_percent(0)
def B_forward(value):
	B2.high()
	B1.low()
	motorB.pulse_width_percent(value)
def B_back(value):
	B1.high()
	B2.low()
	motorB.pulse_width_percent(value)
def B_stop():
	B1.low()
	B2.low()
	motorB.pulse_width_percent(0)

scaleP = 100
scaleD = 10
scaleI = 100
scaleR = 0
#scale = 2.0

while not trigger():	# Wait to tune Kp
	time.sleep(0.001)
	#K_p = pot.read() * scaleP / 4095		# Use potentiometer to set Kp
	#K_p = 9.09
	K_p = 42.3
	oled.draw_text(0, 30, 'Kp={:5.2f}'.format(K_p))	# Display live value on oled
	oled.display()
while trigger(): pass

while not trigger():	# Wait to tune Kd
	time.sleep(0.001)
	#K_d = pot.read() * scaleD / 4095		# Use pot to set Ki
	K_d = 3
	oled.draw_text(0, 40, 'Kd={:5.2f}'.format(K_d))	# Display live value on oled
	oled.display()
while trigger(): pass

while not trigger():	# Wait to tune Ki
	time.sleep(0.001)
	#K_i = pot.read() * scaleI / 4095		# Use pot to set Ki
	K_i = 0
	oled.draw_text(0, 50, 'Ki={:5.2f}'.format(K_i))	# Display live value on oled
	oled.display()
while trigger(): pass

while not trigger():	# Wait to tune offset
	time.sleep(0.001)
	#r = pot.read() * scaleR / 4095		# Use potentiometer to set Kp
	r = -0.5
	oled.draw_text(60, 40, 'r={:5.3f}'.format(r))	# Display live value on oled
	oled.display()
while trigger(): pass

def pitch_estimate(pitch, dt, alpha):
	theta = imu.pitch()
	pitch_dot = imu.get_gy()
	pitch = alpha * (pitch + pitch_dot * dt * 0.000001) + (1 - alpha) * theta
	print(pitch)
	return (pitch, pitch_dot)

alpha = 0.92
pitch = 0
e_int = 0
e_diff = 0
v = 0

tic1 = pyb.micros()
while True:
	dt = pyb.micros() - tic1
	if dt > 5000:
		pitch, pitch_dot = pitch_estimate(pitch, dt, alpha)
		e = pitch - r
		#print('e is:' + str(e))
		# e is corrected angle
		v = -(K_p * e + K_i * e_int + K_d * pitch_dot)
		#print('v is: ' + str(v))
# v is PID control
		e_int += e
		if v > 0:
			A_forward(v)
			B_forward(v)
		if v < 0:
			A_back(-v)
			B_back(-v)

		e_diff = e
		tic1 = pyb.micros()