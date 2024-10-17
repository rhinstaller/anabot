#!/usr/bin/python3

import subprocess
from ponytail.ponytail import Ponytail

try:
    ponytail = Ponytail()
except Exception:
    print ("Fail to initialize Ponytail interfaces")
    exit()

# Start gnome-calculator
subprocess.Popen(["gnome-calculator", "-m", "basic"])
try:
    windowid = ponytail.waitFor("org.gnome.Calculator.desktop", timeout=1)
except ValueError:
    print("No gnome-calculator found")
    exit()

# Connect to the gnome-calculator window
ponytail.connectWindow(windowid)

# Click at (x=100, y=50) - These are buffer coordinates
ponytail.generateButtonEvent(button=1, x=100, y=50)

# Press [1] on the numeric keypad
ponytail.generateKeycodeEvent(87)

for x in [88, 89, 83, 84, 85, 79, 80, 81]:
    # Press [+] on the numeric keypad
    ponytail.generateKeycodeEvent(86)
    ponytail.generateKeycodeEvent(x)
    # Press [Enter] on the numric keypad
    ponytail.generateKeycodeEvent(104)

# Send Alt+F4
ponytail.generateKeycodePress(64)
ponytail.generateKeycodePress(70)
ponytail.generateKeycodeRelease(70)
ponytail.generateKeycodeRelease(64)

# And disconnect
ponytail.disconnect()

