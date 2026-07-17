from rclpy.node import Node
from std_msgs.msg import String
import rclpy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from RPLCD.i2c import CharLCD
import time 
from evdev import InputDevice, categorize, ecodes
import threading
from select import select 

class SheetUpdaterNode(Node):
    def __init__(self):
        super().__init__('sheet_updater_node')

        self.subscription_ = self.create_subscription(String, 'barcode_data', self.callback_barcode, 10)
        self.get_logger().info("Sheet Updater Node has Started")
        self.connect_to_sheet()
        self.lcd = CharLCD('PCF8574', address=0x27, cols = 16, rows = 2)
        
        self.dev = InputDevice('/dev/input/event1')
        self.interrupt_event = threading.Event()
        self.current_barcode = None
        self.quantity_thread = None
        self.lcd.clear()
        self.lcd.write_string("Barcode Reader")
        time.sleep(2)
        self.lcd.clear()
        self.lcd.write_string("Scan Barcode : ")

    def connect_to_sheet(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        current_dir = os.path.dirname(os.path.realpath(__file__))
        credentials_path = os.path.join(current_dir, 'credentials.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scopes)
        client = gspread.authorize(creds)
        self.sheet = client.open_by_key("17kp2SenMBsS8jV8uFnb3AwnHL5KCjFg0CV25Y6GJ3hM").sheet1
        self.get_logger().info("Connected to Google Sheet")



    def callback_barcode(self, msg):
        barcode = msg.data.strip()
         
        #THis is before adding the part where same chemical can be scanned afeter entering the quantity 
        if barcode == self.current_barcode:
            self.get_logger().info(f"Ignoring duplicate barcode: {barcode}")
            return 
        
        self.get_logger().info(f"New barcode received: {barcode}")
        self.current_barcode = barcode

        if self.quantity_thread and self.quantity_thread.is_alive():
            self.interrupt_event.set()
            self.quantity_thread.join()
            self.interrupt_event.clear()

        # self.interrupt_event.clear()

        self.quantity_thread = threading.Thread(target=self.handle_barcode, args=(barcode,))
        self.quantity_thread.start()

    def handle_barcode(self, barcode):
        if self.interrupt_event.is_set():
            return 
        
        barcodes = self.sheet.col_values(2)
        try:
            row_index = barcodes.index(barcode) + 1
            chemical_name = self.sheet.cell(row_index, 1).value
            chemical_quantity_str = self.sheet.cell(row_index, 3).value
            self.get_logger().info(f"Chemical: {chemical_name}")
            self.get_logger().info(f"Quantity: {chemical_quantity_str}")
            try:
                chemical_quantity = float(chemical_quantity_str)
            except ValueError:
                self.get_logger().error("Invalid format in spreadsheet")
                self.lcd.clear()
                return
            self.lcd.clear()
            self.lcd.write_string(chemical_name)
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string("Qty:" + str(chemical_quantity))
            time.sleep(1.5)
            if self.interrupt_event.is_set():
                return 

            self.lcd.clear()
            self.lcd.write_string(chemical_name)
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string("Enter Quantity:")
            qty_num = self.get_quantity_from_numpad(self.dev)

            if self.interrupt_event.is_set():
                return 

            if qty_num == 'CANCEL':
                self.get_logger().info("User cancelled")
                self.lcd.clear()
                self.lcd.write_string("Scan Barcode : ")
                self.current_barcode = None 
                return
                
            if qty_num is not None and qty_num != "":
                try:
                    qty = float(qty_num)
                except ValueError:
                    self.get_logger().warn(f"Invalid float entered: {qty_num}")
                    return
            else:
                self.get_logger().warn("No valid quantity")
                return
            self.lcd.clear()
            self.lcd.write_string(chemical_name)
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string("Used : " + str(qty))
            time.sleep(1)
            self.lcd.clear()
            new_qty = chemical_quantity - qty
            self.lcd.write_string(chemical_name)
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string("Remaining : " + str(new_qty))
            self.sheet.update_cell(row_index, 3, new_qty)
            time.sleep(1)
            self.lcd.clear()
            self.lcd.write_string("Scan Barcode : ")
            self.current_barcode = None
            self.get_logger().info("callback_end")
        except ValueError:
            self.get_logger().warn(f"Barcode '{barcode}' not found in Column B.")

    def get_quantity_from_numpad(self,dev):
        quantity = ""
        key_map = {
        'KEY_KP0' : '0',
        'KEY_KP1' : '1',
        'KEY_KP2' : '2',
        'KEY_KP3' : '3',
        'KEY_KP4' : '4',
        'KEY_KP5' : '5',
        'KEY_KP6' : '6',
        'KEY_KP7' : '7',
        'KEY_KP8' : '8',
        'KEY_KP9' : '9',
        'KEY_BACKSPACE' : 'BACKSPACE',
        'KEY_ENTER': 'ENTER',
        'KEY_KPENTER': 'ENTER',
        'KEY_0' : '0',
        'KEY_1' : '1',
        'KEY_2' : '2',
        'KEY_3' : '3',
        'KEY_4' : '4',
        'KEY_5' : '5',
        'KEY_6' : '6',
        'KEY_7' : '7',
        'KEY_8' : '8',
        'KEY_9' : '9',
        'KEY_KPDOT' : '.',
        'KEY_DOT' : '.',
        'KEY_KPASTERISK' : 'CANCEL'
        }
        self.get_logger().info("Waiting for input info")
        while not self.interrupt_event.is_set():
            r, _, _ = select([dev.fd], [], [], 0.1)
            if not r:
                continue
            for event in dev.read():
                if event.type == ecodes.EV_KEY and event.value == 1:
                    key_event = categorize(event)
                    code = key_event.keycode
                    if isinstance(code, list):
                        code = code[0]
                    mapped = key_map.get(code, None)
                    if mapped == 'ENTER':
                        return quantity if quantity else None
                    elif mapped == 'BACKSPACE':
                        quantity = quantity[:-1]
                    elif mapped is not None:
                        quantity += mapped
                    self.lcd.cursor_pos = (1,0)
                    self.lcd.write_string(" "*16)
                    self.lcd.cursor_pos = (1,0)
                    self.lcd.write_string(quantity)
                    
    
            
        return None
        # done = False
        # if self.interrupt_event.is_set():
        #         return 
        # while not done:
        #     self.get_logger().info("Detected key event")
        #     for event in dev.read_loop():
        #         if self.interrupt_event.is_set():
        #             self.get_logger().info("Input interrupted by new barcode")
                    
        #             return None 
                
                
                
        #         if event.type == ecodes.EV_KEY and event.value == 1:
        #             key_event = categorize(event)
        #             code = key_event.keycode
        #             if isinstance(code, list):
        #                 code = code[0]

        #             mapped = key_map.get(code, None)
        #             if mapped == 'ENTER':
        #                 done = True
        #                 break
        #             elif mapped == 'BACKSPACE':
        #                 quantity = quantity[:-1]
        #             elif mapped is not None:
        #                 quantity += mapped
        #             self.lcd.cursor_pos = (1,0)
        #             self.lcd.write_string(" "*16)
        #             self.lcd.cursor_pos = (1,0)
        #             self.lcd.write_string(quantity)
                    
        #     if done:
        #         break
 
        
        # return quantity if quantity else None

def main():
    rclpy.init()
    node = SheetUpdaterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()