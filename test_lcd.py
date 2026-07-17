from RPLCD.i2c import CharLCD
import time

lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

lcd.clear()
lcd.write_string("It works")
time.sleep(5)
lcd.clear()
lcd.write_string("Line 1")
lcd.cursor_pos = (1,0)
lcd.write_string("Line 2")
time.sleep(5)
lcd.clear()