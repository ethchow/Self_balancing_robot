'''
-------------------------------------------------------
Name: Milestone 3 - Dance routine
Creator:  Group 15
Date:   24/02/2020
-------------------------------------------------------
Simple dance with stabilizer

Dance routine
-------------------------------------------------------
'''
import pyb
#from random import randint
#import random
from pyb import Pin, Timer, ADC, DAC, LED
import time
from array import array
from oled_938 import OLED_938	# Use OLED display driver
import micropython

micropython.alloc_emergency_exception_buf(100)

# Setup OLED display
oled = OLED_938(pinout={'sda': 'Y10', 'scl': 'Y9', 'res': 'Y8'}, height=64,
                   external_vcc=False, i2c_devid=61)
oled.poweron()
oled.init_display()
oled.draw_text(0,0, 'Group 15')
oled.draw_text(0, 10, 'Milestone 3: Beat Detection')
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

A1 = Pin('X3',Pin.OUT_PP)	# A is right motor
A2 = Pin('X4',Pin.OUT_PP)
B1 = Pin('X7',Pin.OUT_PP)	# B is left motor
B2 = Pin('X8',Pin.OUT_PP)
PWMA = Pin('X1')
PWMB = Pin('X2')

tim = Timer(2, freq = 10000)
motorA = tim.channel(1, Timer.PWM, pin = PWMA)
motorB = tim.channel(2, Timer.PWM, pin = PWMB)

mic = ADC(Pin('Y11'))
MIC_OFFSET = 1523
dac = pyb.DAC(1, bits=12)
b_LED = LED(4)        #flash for beats on blue LED

N = 160				# size of sample buffer
s_buf = array('H', 0 for i in range(N))  # reserve buffer memory
ptr = 0				# buffer index
buffer_full = False	# semaphore - ISR communicate with main program

def flash():
	b_LED.on()
	pyb.delay(30)
	b_LED.off()

def energy(buf):	# Compute energy of signal in buffer
	sum = 0
	for i in range(len(buf)):
		s = buf[i] - MIC_OFFSET	# adjust sample to remove dc offset
		sum = sum + s*s			# accumulate sum of energy
	return sum


def isr_sampling(dummy): 	# timer interrupt at 8kHz
	global ptr				# need to make ptr visible inside ISR
	global buffer_full		# need to make buffer_full inside ISR

	s_buf[ptr] = mic.read()	# take a sample every timer interrupt
	ptr += 1				# increment buffer pointer (index)
	if (ptr == N):			# wraparound ptr - goes 0 to N-1
		ptr = 0
		buffer_full = True	# set the flag (semaphore) for buffer full


sample_timer = pyb.Timer(7, freq=8000)
sample_timer.callback(isr_sampling)

M = 50                      # number of instantaneous energy epochs to sum
BEAT_THRESHOLD = 4      # threshold for c to indicate a beat
SILENCE_THRESHOLD = 1.2    # threshold for c to indicate silence

e_ptr = 0                   # pointer to energy buffer
e_buf = array('L', 0 for i in range(M)) # reserve storage for energy buffer
sum_energy = 0              # total energy in last 50 epochs
oled.draw_text(0,20, 'Ready to GO') # Useful to show what's happening?
oled.display()


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


def dance():
	n = pyb.rng()%10+1
	#n = 1
	if n == 1:
		print('forward')
		A_forward(75)
		B_forward(75)
	if n == 2:
		print('backwards')
		A_back(75)
		B_back(75)
	if n == 3:
		print('left turn')
		A_forward(75)
		B_forward(0)
	if n == 4:
		print('right turn')
		A_forward(0)
		B_forward(75)
	if n == 5:
		print('bare left forward')
		A_forward(75)
		B_forward(30)
	if n == 6:
		print('bare right forward')
		A_forward(30)
		B_forward(75)
	if n == 7:
		print('bare right back')
		A_back(75)
		B_back(30)
	if n == 8:
		print('bare left back')
		A_back(30)
		B_back(75)
	if n == 9:
		print('clockwise spin')
		A_forward(75)
		B_back (75)
	if n == 10:
		print('anticlockwise spin')
		A_back(75)
		B_forward(75)
	if n == 11:
		print('forward back')
		A_back(90)
		B_forward(90)
		pyb.delay(500)
		A_back(0)
		B_forward(0)
		A_forward(90)
		B_back(90)
		pyb.delay(500)


# MAIN FUNCTION

tic = pyb.millis()

while True:
	if buffer_full:
		E = energy(s_buf)     # compute moving sum of last 50 energy epochs
		sum_energy = sum_energy - e_buf[e_ptr] + E
		e_buf[e_ptr] = E
		# over-write earliest energy with most recent
		e_ptr = (e_ptr + 1) % M # increment e_ptr with wraparound - 0 to M-1
		# Compute ratio of instantaneous energy/average energy
		c = E*M/sum_energy
		dac.write(min(int(c*4095/3), 4095))     # useful to see on scope, can remove

		if pyb.millis()-tic > 500:    # if more than 500ms since last beat
			if c > BEAT_THRESHOLD:      # look for a beat
				flash()
				dance()                     # beat found, flash blue LED
				tic = pyb.millis()      # reset tic
		dac.write(0)                    # useful to see on scope, can remove
		buffer_full = False             # reset status flag