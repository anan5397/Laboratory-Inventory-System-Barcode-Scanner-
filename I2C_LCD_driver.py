import smbus2
import time

# For Raspberry Pi, bus 1 is usually the default I2C bus
bus = smbus2.SMBus(1)

# PCF8574 default address is 0x27 or 0x3F depending on the module
ADDRESS = 0x27

# LCD commands
LCD_WIDTH = 16   # Characters per line
LCD_CHR = 1     # Mode - Sending data
LCD_CMD = 0     # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT = 0x08

ENABLE = 0b00000100

def lcd_strobe(data):
    bus.write_byte(ADDRESS, data | ENABLE | LCD_BACKLIGHT)
    time.sleep(0.0005)
    bus.write_byte(ADDRESS, ((data & ~ENABLE) | LCD_BACKLIGHT))
    time.sleep(0.0001)

def lcd_write_byte(bits, mode):
    high_bits = mode | (bits & 0xF0) | LCD_BACKLIGHT
    low_bits = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    bus.write_byte(ADDRESS, high_bits)
    lcd_strobe(high_bits)

    bus.write_byte(ADDRESS, low_bits)
    lcd_strobe(low_bits)

def lcd_init():
    lcd_write_byte(0x33, LCD_CMD)  # Initialise
    lcd_write_byte(0x32, LCD_CMD)  # Initialise
    lcd_write_byte(0x06, LCD_CMD)  # Cursor move direction
    lcd_write_byte(0x0C, LCD_CMD)  # Turn cursor off
    lcd_write_byte(0x28, LCD_CMD)  # 2 line display
    lcd_write_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(0.0005)

def lcd_clear():
    lcd_write_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(0.002)

def lcd_display_string(message, line):
    if line == 1:
        lcd_write_byte(LCD_LINE_1, LCD_CMD)
    elif line == 2:
        lcd_write_byte(LCD_LINE_2, LCD_CMD)

    for char in message.ljust(LCD_WIDTH):
        lcd_write_byte(ord(char), LCD_CHR)
