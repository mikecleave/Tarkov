import pyautogui as pya
import pydirectinput #https://github.com/learncodebygaming/pydirectinput
import time
import keyboard
import sys
from sendKeys import *
from threading import Thread

pya.FAILSAFE = True #When fail-safe mode is True, moving the mouse to the upper-left will raise a pyautogui.FailSafeException that can abort your program

keys = { # msdn.microsoft.com/en-us/library/dd375731
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "a": 0x41,
    "c": 0x43,
    "d": 0x44,
    "q": 0x51,
    "s": 0x53,    
    "w": 0x57, 
    "y": 0x59, 
    "f9": 0x78,
    "space": 0x20
}

pya.size()
centerScreen = pya.size()
centerScreen = centerScreen.width/2, centerScreen.height/2 - 15


def main():
    while keyboard.is_pressed('i') == False: #If 'i' is pressed it will stop the program. 
        print('checking for purchase button')
        if pya.locateOnScreen('img/purchase.png') != None:
            print('purchase button found')
            pya.moveTo(pya.locateOnScreen('img/purchase.png'))
            pya.click()
            SendKey(keys['y'])
            sys.exit("Purchase Complete")
           

def killSwitchCheck():
    if keyboard.is_pressed('i') == True: #Check if I want to stop the program
        releaseAllKeys()        
        sys.exit("Program manually stopped")

def placeChest(direction):
    print('place chest')
    horizontalOffset = 0
    verticalOffset = 0

    if direction == "a":
        horizontalOffset = 30

    elif direction == "d":
        horizontalOffset = -30

    elif direction == "w":
        verticalOffset = 30

    elif direction == "s":
        verticalOffset = -30
    
    SendKey(keys['1'])
    pya.moveTo(centerScreen[0]+horizontalOffset, centerScreen[1]+verticalOffset)    
    pya.click()
    SendKey(keys['q'])


time.sleep(3)
print("Start")
main()
print("Done")