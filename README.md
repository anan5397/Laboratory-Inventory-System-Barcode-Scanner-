ROS2 Chemical Inventory Management System

A ROS2-based laboratory chemical inventory management system developed on Raspberry Pi. The system uses barcode scanning to identify chemicals, retrieves inventory information, allows users to record chemical usage through a keypad, updates stock levels, and displays real-time information through an LCD interface.

This project demonstrates ROS2 communication architecture, embedded hardware integration, IoT database management, and automation for laboratory environments.

Features
Barcode-based chemical identification
ROS2 publisher/subscriber communication
Real-time inventory tracking
LCD user interface
Numpad quantity input
Automatic stock calculation
Google Sheets database integration
Raspberry Pi hardware integration
System Architecture
                 USB Barcode Scanner
                         |
                         |
                         v
              barcode_reader_node
                         |
                         |
              ROS2 Topic: /barcode_data
                         |
                         |
                         v
              sheet_updater_node
                         |
          -----------------------------
          |                           |
          v                           v
    Google Sheets                 LCD Display
    Inventory Database            User Interface
          
                         ^
                         |
                      Numpad
                Quantity Input
ROS2 Nodes
1. Barcode Reader Node
barcode_reader_node.py

Responsible for interfacing with the USB barcode scanner.

Functions:

Reads scanner input using Linux evdev
Converts keyboard events into barcode strings
Publishes barcode information through ROS2 topic

Publishes:

Topic:
/barcode_data

Message Type:
std_msgs/String

Example message:

data: "CHEM00123"
2. Inventory Management Node
sheet_updater_node.py

Responsible for managing chemical information and updating inventory.

Functions:

Subscribes to barcode data
Searches chemical information from database
Displays chemical name and quantity on LCD
Receives consumed quantity from numpad
Calculates remaining stock
Updates inventory database
Workflow
User scans chemical barcode
Barcode Scanner
        |
        v
CHEM00123
Barcode is published through ROS2:
/barcode_data
System retrieves chemical information:

Example:

Chemical:
Hydrochloric Acid

Current Quantity:
500 mL
User enters consumed amount:
Used:
50 mL
System updates inventory:
Remaining:
450 mL
Database is updated automatically.
Hardware
Component	Purpose
Raspberry Pi	Main controller
USB Barcode Scanner	Chemical identification
16x2 I2C LCD	User interface
USB Numpad	Quantity input
Software
Technology	Purpose
ROS2	Node communication framework
Python	Application development
Google Sheets API	Inventory database
RPLCD	LCD control
evdev	Linux input handling
Installation
Requirements
Raspberry Pi running Linux
ROS2 installed
Python 3
USB barcode scanner
I2C LCD

Install Python dependencies:

pip install rclpy
pip install gspread
pip install oauth2client
pip install RPLCD
pip install evdev
Running the Project

Build ROS2 workspace:

colcon build

Source environment:

source install/setup.bash

Run barcode node:

ros2 run <package_name> barcode_reader_node

Run inventory node:

ros2 run <package_name> sheet_updater_node
Future Improvements
Replace Google Sheets with SQLite database for offline operation
Integrate CLEAPSS chemical safety knowledge base using RAG
Add voice assistant interface
Add automatic chemical cabinet location tracking
Develop web dashboard for inventory monitoring
Project Motivation

Laboratory chemical management requires accurate inventory tracking and safety information access. This project explores how ROS2 and IoT technologies can automate laboratory workflows and improve chemical management efficiency.
