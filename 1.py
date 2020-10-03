'''
-------------------------------------------------------
Name: Milestone 1 - Bluetooth
Creator:  Group 15
Date:   24/02/2020
-------------------------------------------------------
Drive motor via BlueFruit UART
-------------------------------------------------------
'''
import pyb
from pyb import Pin, Timer, ADC, UART
import time
from oled_938 import OLED_938	# Use OLED display driver

import micropython
micropython.alloc_emergency_exception_buf(100)
# Setup OLED display
oled = OLED_938(pinout={'sda': 'Y10', 'scl': 'Y9', 'res': 'Y8'}, height=64,
                   external_vcc=False, i2c_devid=61)
oled.poweron()
oled.init_display()
oled.draw_text(0,0, 'Group 15')
oled.draw_text(0, 10, 'Milestone 1: Bluetooth')
oled.draw_text(0, 20, 'Press USR button')
oled.display()
print('Performing Milestone 1')
print('Waiting for button press')

# Trigger setup
trigger = pyb.Switch()
while not trigger():
    time.sleep(0.001)
while trigger():
    pass
print('Button pressed - Running')
oled.draw_text(0,30, 'Running Milestone 1')
oled.display()

# Setting up the motors
A1 = Pin('X3',Pin.OUT_PP)	# A is right motor
A2 = Pin('X4',Pin.OUT_PP)
B1 = Pin('X7',Pin.OUT_PP)	# B is left motor
B2 = Pin('X8',Pin.OUT_PP)
PWMA = Pin('X1')
PWMB = Pin('X2')

tim = Timer(2, freq = 1000)
motorA = tim.channel (1, Timer.PWM, pin = PWMA)
motorB = tim.channel (2, Timer.PWM, pin = PWMB)

pot = pyb.ADC(Pin('X11'))

uart = UART(6)
uart.init(9600, bits=8, parity = None, stop = 2)

# Define motor controls
def A_forward(value):
	A1.low()
	A2.high()
	motorA.pulse_width_percent(value)
def A_back(value):
	A2.low()
	A1.high()
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

# Use keypad U and D keys to control speed
DEADZONE = 5
speed = 0

# --- Main program loop --- #
while True: 	# loop forever until CTRL-C
	speed = int((pot.read() - 2048) * 200 / 4096) # control speed with potentiometer

	while (uart.any()!=5):    # wait for 10 chars
		pass
	command = uart.read(5)
	if command[3] ==ord('1'):
		if command[2]==ord('7'):
			oled.draw_text(0, 40, 'Motor Drive:{:d}'.format(command[2]))
			A_forward(speed)
			B_forward(speed)
		elif command[2]==ord('8'):
			oled.draw_text(0, 40, 'Motor Drive:{:d}'.format(command[2]))
			A_back(speed)
			B_back(speed)
		elif command[2]==ord('6'):
			oled.draw_text(0, 40, 'Motor Drive:{:d}'.format(command[2]))
			A_forward(speed)
			B_back(speed)
		elif command[2] ==ord('5'):
			oled.draw_text(0, 40, 'Motor Drive:{:d}'.format(command[2]))
			A_back(speed)
			B_forward(speed)
	elif command[3] ==ord('0'):
		if command[2] ==ord('5') or command[2] ==ord('6') or command[2] ==ord('7') or command[2] ==ord('8'):
			oled.draw_text(0, 40, 'Motor Drive:{:d}'.format(command[3]))
			A_stop()
			B_stop()

	oled.display()
