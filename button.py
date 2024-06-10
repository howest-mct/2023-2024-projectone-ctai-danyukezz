from RPi import GPIO
import time
GPIO.setmode(GPIO.BCM)

button = 25
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
try:
    while True:
        button_state = GPIO.input(button)
        if button_state is GPIO.LOW:
            print('not pressed')
        elif button_state is GPIO.HIGH:
            print('pressed')
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()