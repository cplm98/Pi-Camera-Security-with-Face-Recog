#*****motionDetector.py*****#
import RPi.GPIO as GPIO
import time

Blue = 11
Red = 12
Green = 13
Pir= 16

# pin setup
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(Blue, GPIO.OUT)
GPIO.setup(Red, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)
GPIO.setup(Pir, GPIO.IN)

def lightOff():
    GPIO.output(Red, 1)
    GPIO.output(Green, 1)
    GPIO.output(Blue, 1)
    time.sleep(.3)

def lightOn():
    GPIO.output(Red, 0)
    GPIO.output(Green, 0)
    GPIO.output(Blue, 0)
    time.sleep(.3)


while True:
    i = GPIO.input(Pir) # read pir value
    if i==0:
        print("No Intruders")
        lightOff()
    elif i==1:
        print("Intruder Detected")
        lightOn()
