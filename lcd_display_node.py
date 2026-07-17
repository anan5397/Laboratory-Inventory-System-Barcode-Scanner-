from RPLCD.i2c import CharLCD
import rclpy 
from rclpy.node import Node


class LcdDisplayNode(Node):
    def __init__(self):
        super().__init__('lcd_display_node')
       
        
        lcd = CharLCD('PCF8574', 0x27)

        lcd.clear()
        lcd.write_string("Hello World!")


def main(args=None):
    rclpy.init(args=args)
    node = LcdDisplayNode()
    node.destroy_node()
    rclpy.shutdown()




