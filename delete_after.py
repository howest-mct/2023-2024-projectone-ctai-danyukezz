import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


pins_to_reset = [8]  # Add more pins if needed


try:
    for pin in pins_to_reset:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    print("Cleanup")
    GPIO.cleanup()