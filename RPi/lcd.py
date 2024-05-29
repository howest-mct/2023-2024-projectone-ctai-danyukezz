import smbus
import time
import subprocess
from RPi import GPIO
GPIO.setmode(GPIO.BCM)
i2c = smbus.SMBus(1)
import threading
import queue
import time


class LCD:
    def __init__(self, I2C_ADDR = 0x27, LCD_WIDTH = 16, LCD_CHR = 0b1, LCD_CMD = 0b0, LCD_LINE_1 = 0x80, LCD_LINE_2 = 0xC0, E_PULSE = 0.0002, E_DELAY = 0.0002, button = 7) -> None:
        self.__I2C_ADDR = I2C_ADDR
        self.__LCD_WIDTH = LCD_WIDTH
        self.__LCD_CHR = LCD_CHR
        self.__LCD_CMD = LCD_CMD
        self.__LCD_LINE_1 = LCD_LINE_1
        self.__LCD_LINE_2 = LCD_LINE_2
        self.__E_PULSE = E_PULSE
        self.__E_DELAY = E_DELAY
        self.__button = button

    def button(self):
        return self.__button
    
    def set_data_bits(self, value, mode): # mode instruction or data
        MSNibble = value & 0xf0
        LSNibble = (value & 0xf) << 4

        time.sleep(self.__E_DELAY)
        i2c.write_byte(self.__I2C_ADDR, MSNibble | (0b1100) | mode)
        time.sleep(self.__E_PULSE)
        i2c.write_byte(self.__I2C_ADDR, MSNibble | (0b1000) | mode)
        time.sleep(self.__E_DELAY)
        i2c.write_byte(self.__I2C_ADDR, LSNibble | (0b1100) | mode)
        time.sleep(self.__E_PULSE)
        i2c.write_byte(self.__I2C_ADDR, LSNibble | (0b1000) | mode) 
        time.sleep(self.__E_DELAY)

    def send_instruction(self, byte):
        self.set_data_bits(byte, self.__LCD_CMD)
        time.sleep(0.01)

    def send_character(self, byte):
        self.set_data_bits(byte, self.__LCD_CHR)
        time.sleep(0.01)

    def send_byte_with_e_toggle(self, bits):
        #Toggle enable
        time.sleep(self.__E_DELAY)
        i2c.write_byte(self.__I2C_ADDR, bits | 0b00000100)
        time.sleep(self.__E_PULSE)
        i2c.write_byte(self.__I2C_ADDR, bits | 0b11111011) 
        time.sleep(self.__E_DELAY)

    def clear(self):
        self.send_instruction(0x01)

    def lcd_init(self):
        self.send_byte_with_e_toggle(0b0011_0000)
        self.send_byte_with_e_toggle(0b0011_0000)
        self.send_byte_with_e_toggle(0b0010_0000)
        
        self.send_instruction(0x28)
        self.send_instruction(0x06) 
        self.send_instruction(0x0C) 
        self.clear()

    def send_string(self, message, line):
        self.send_instruction(line)

        for char in message:
            self.send_character(ord(char))

    # ********** property LCD_LINE_1 - (setter/getter) ***********
    @property
    def LCD_LINE_1(self) -> int:
        """ The LCD_LINE_1 property. """
        return self.__LCD_LINE_1
    
    @LCD_LINE_1.setter
    def LCD_LINE_1(self, value: int) -> None:
        self.__LCD_LINE_1 = value
    
    @property
    def LCD_LINE_2(self) -> type:
        """ The LCD_LINE_2 property. """
        return self.__LCD_LINE_2
    
    