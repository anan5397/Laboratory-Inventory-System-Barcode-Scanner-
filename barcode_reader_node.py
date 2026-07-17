import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import re 
from evdev import InputDevice, categorize, ecodes
import threading

class BarcodeReaderNode(Node):
    def __init__(self):
        super().__init__('barcode_reader_node')
        self.publisher_ = self.create_publisher(String, 'barcode_data', 10)
        self.get_logger().info("Barcode Reader Node Started")
        self.device = InputDevice('/dev/input/event0')
        self.buffer = ""
        # self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        # self.read_thread.start()
        
        
        self.timer = self.create_timer(0.01, self.read_loop)
       
    def read_loop(self):
        for event in self.device.read_loop():            
            if event.type == ecodes.EV_KEY and event.value == 1:
                key_event = categorize(event)                   
                keycode = key_event.keycode

                if isinstance(keycode, list):
                    keycode = keycode[0]

                if keycode == 'KEY_ENTER':
                    cleaned = ''.join(char for char in self.buffer if char.isalnum())
                    if cleaned:
                        msg = String()
                        msg.data = cleaned
                        self.publisher_.publish(msg)
                        self.get_logger().info(f"Published: {cleaned}")
                    self.buffer = ""
                else:
                    char = self.keycode_to_char(keycode)
                    if char:
                        self.buffer += char

    def keycode_to_char(self, keycode):
        key_map = {
            'KEY_0' : '0','KEY_1' : '1','KEY_2' : '2','KEY_3' : '3',
            'KEY_4' : '4','KEY_5' : '5','KEY_6' : '6','KEY_7' : '7',
            'KEY_8' : '8','KEY_9' : '9','KEY_A' : 'A','KEY_B': 'B',
            'KEY_C': 'C','KEY_D' : 'D','KEY_E' : 'E','KEY_F' : 'F',
            'KEY_G' : 'G','KEY_H' : 'H','KEY_I' : 'I','KEY_J' : 'J',
            'KEY_K' : 'K','KEY_L' : 'L','KEY_M' : 'M','KEY_N' : 'N',
            'KEY_O': 'O','KEY_P': 'P','KEY_Q' : 'Q','KEY_R' : 'R',
            'KEY_S' : 'S','KEY_T' : 'T','KEY_U' : 'U','KEY_V' : 'V',
            'KEY_W' : 'W','KEY_X' : 'X','KEY_Y' : 'Y','KEY_Z' : 'Z',   
        }
        return key_map.get(keycode,'')
     


def main(args=None):
    rclpy.init(args=args)
    node = BarcodeReaderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Reader interrupted")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()