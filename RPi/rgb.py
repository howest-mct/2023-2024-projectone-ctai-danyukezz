from RPi import GPIO
import smbus
from time import sleep

class Rgb:
    
    def __init__(self, rgb_r=5, rgb_g=6, rgb_b=13) -> None:
        self.__rgb_r = rgb_r
        self.__rgb_g = rgb_g
        self.__rgb_b = rgb_b
        
        # Setup GPIO pins
        GPIO.setup(self.__rgb_r, GPIO.OUT)
        GPIO.setup(self.__rgb_g, GPIO.OUT)
        GPIO.setup(self.__rgb_b, GPIO.OUT)
        
        # Initialize PWM
        self.__rgb_r_pwm = GPIO.PWM(self.__rgb_r, 1000)
        self.__rgb_g_pwm = GPIO.PWM(self.__rgb_g, 1000)
        self.__rgb_b_pwm = GPIO.PWM(self.__rgb_b, 1000)
    
    def setup(self):
        self.__rgb_r_pwm.start(100)
        self.__rgb_g_pwm.start(100)
        self.__rgb_b_pwm.start(100)

    def control_rgb(self, data_x, data_y, data_z):
        self.__rgb_r_pwm.ChangeDutyCycle(100 - data_x / 255 * 100)
        self.__rgb_g_pwm.ChangeDutyCycle(100 - data_y / 255 * 100)
        self.__rgb_b_pwm.ChangeDutyCycle(100 - data_z / 255 * 100)
    
    def cleanup(self):
        self.__rgb_r_pwm.stop()
        self.__rgb_g_pwm.stop()
        self.__rgb_b_pwm.stop()
        GPIO.cleanup()
