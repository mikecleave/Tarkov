#This is to be run full screen on my larger monitor. 
#You must use the Woods background menu screen.

"""
*** To DO ***
1. Update code to use % of screen instead of hard coded coordinates. This will allow my program to work on all monitors. Not sure if this is actually needed...
2. Add a msg  box that the program has stopped when the user moves their cursor to the top left of the screen. 
2. If I run out of money, I need to accept the money from Ragman. 
2. When buying an item, check the quantity I am buying to I can create a summary report. Or instead, only check how many items I list when I sell them on the flee. 
2. When I buy an item from fence, I need to keep buying it until its out of stock before switching to the next item. 
2. Esmarch improvments:
    - If I am only buying esmarches, I should not bother refreshing the stock if there is 1 image on the screen. Will allow me to buy them faster. 

3. Buy bandages:
    - Fence sells them for 1893 rubles. 
    - Check the market to see the current price. If it is below the minimum, don't buy and sell any. 
    - Check if I already have a listing. If I do, don't buy and sell any.
    - If I am going to buy them, I want to make sure my inventory is empty as possible so I can do 1 large bulk sell. Need to sell off other items first before I start buying.
    - 

4. Once I have higher lvl traders, buy and resell their items:
    - Check the min flee sell price and see the difference between the buy price from the trader.
    - Buy gernades every reset.      
5. Make a debug version where I draw a red box around the image I am trying to click. 
"""

"""
HOW TO PACKAGE:
Open a command prompt/shell window, and navigate to the directory where your .py file is located, then build your app with the following command:
pyinstaller --onedir --add-data "Img:Img" --contents-directory "." Market.py
"""
import sys
import pyautogui
import cv2
import numpy as np
import time
from datetime import datetime
from screeninfo import get_monitors
import pytesseract

from PIL import Image, ImageDraw

import tkinter as tk
from tkinter import Canvas
from tkinter import messagebox
root = tk.Tk()
root.withdraw()  # Hides the root window

import re

traderStoreRegion = (0, 0, 700, 1000)
fleeSellingRegion = (0, 0, 650, 800) #Your flee selling windown needs to be in the top left corner.
#CaptchaTextRegion = (777, 365, 372, 26)
CaptchaImageRegion = (684, 230, 546, 813)

stashFull = False

#https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Mike\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def DrawRedBox(region):
    x = region[0]
    y = region[1]
    width = region[2]
    height = region[3]
    # Capture the current screen using pyautogui
    screenshot = pyautogui.screenshot()

    # Convert the screenshot to a format OpenCV can work with (numpy array)
    img = np.array(screenshot)

    # Convert the image to BGR format (OpenCV uses BGR, while PIL uses RGB)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Define the top-left and bottom-right corners of the rectangle
    top_left = (x, y)
    bottom_right = (x + width, y + height)

    # Overlay a red rectangle (BGR color for red is (0, 0, 255)) with thickness of 2 pixels
    cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), thickness=2)

    # Display the image with the red box
    cv2.imshow("Screen with Red Box", img)

    # Wait for the user to press any key and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Find the location of the image on the screen
def FindImageOnScreen(imageName, region=None, grayscale=False):
    template_path = f"Img/{imageName}.png"    
    #print("Start Looking")
    imageLocation = pyautogui.locateOnScreen(template_path, region=region, grayscale=grayscale, confidence=.8)
    #print(imageLocation)
    #print("Stop Looking")
    if imageLocation is not None:
        imageCenter = pyautogui.center(imageLocation)
        return imageCenter
    else:
        return imageLocation

def ClickAndHold(x, y, duration = 3):
    pyautogui.moveTo(x, y)
    #print("Mouse Down")
    pyautogui.mouseDown()
    time.sleep(duration)
    #print("Mouse Up")
    pyautogui.mouseUp()

def Click(x, y, delay):
    time.sleep(delay)  # Add delay before the click
    pyautogui.moveTo(x, y)
    pyautogui.click()
    #time.sleep(delay)  # Add delay after the click

# Get the dimensions of the monitor
def GetMonitorRegion():
    monitors = get_monitors()
    if len(monitors) > 1:
        print("2 monitors detected")
        monitor = monitors[0] #Use 0 for primary and 1 for secondary monitor.
        screenRegion = monitor.x, monitor.y, monitor.width, monitor.height
        print(screenRegion)
        return screenRegion
    else:
        print("Second monitor not detected")
        monitor = monitors[0] #*** May have to change this to 0 or 1 *** 
        screenRegion = monitor.x, monitor.y, monitor.width, monitor.height
        print(screenRegion)
        return screenRegion

def ClickImage(imageName, delay=1, region=None, grayscale=False):
    position = FindImageOnScreen(imageName, region, grayscale=grayscale)
    if position:
        print(f"Found {imageName} at: {position}")
        Click(position[0], position[1], delay)
        return True
    else:
        print(f"{imageName} not found on the screen.")
        return False

def MustClickImage(imageName, delay=1, region=None):
    successfull = False
    while not successfull:
        position = FindImageOnScreen(imageName, region)
        if position:
            print(f"Found {imageName} at: {position}")
            Click(position[0], position[1], delay)
            successfull = True
        else:
            print(f"{imageName} not found on the screen.")

def ScrollToClick(imageName, delay=1, region=None):
    successfull = False

    # Scroll until the item is found OR you reach the bottom. 
    while not successfull and (not ClickImage("ScrollBottom", 0.01)):
        position = FindImageOnScreen(f"Img/{imageName}.png", region)
        if position:
            print(f"Found {imageName} at: {position}")
            Click(position[0], position[1], delay)
            successfull = True
        else:
            print(f"{imageName} not found on the screen. Scrolling down")
            pyautogui.moveTo(region)
            pyautogui.scroll(-5000) #Scroll down

def PreprocessImage(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply thresholding to binarize the image
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def ImageRecognition(captureRegion):
    # Take a screenshot of the specified captureRegion
    screenshot = pyautogui.screenshot(region=captureRegion)

    # Save the screenshot
    imageFilePath = 'C:/Users/Mike/Documents/Tarkov/Screenshots/screenshot.png'
    screenshot.save(imageFilePath)
    #print(f"Screenshot saved to: {imageFilePath}")
    
    # Load the captured screenshot image
    #image = Image.open(imageFilePath)
    image = cv2.imread(imageFilePath)

    # Preprocess the image
    #PreprocessedImage = PreprocessImage(image)

    # Use Tesseract to do OCR on the image
    customConfig = r'--oem 3 --psm 6 tessedit_char_whitelist=0123456789₽'
    number = pytesseract.image_to_string(image, config=customConfig)
    number = number[1:] #Removes the fist number since the image recognition thinks the curancy symbol is a '2'
    
    # Remove any unwanted characters like 'P', and newlines, leaving digits
    cleaned_number = re.sub(r'[^0-9]', '', number).strip()
    
    try:
        # Convert the cleaned string to a float, then to an integer to remove decimal places
        #number_int = int(float(cleaned_number))
        
        # Format as currency without decimal places and add the ruble symbol
        #formatted_number = f"₽{number_int:,}"
        #return formatted_number
        return cleaned_number
    except ValueError:
        print(f"The OCR result '{number}' could not be converted to a valid number.")
        return 0
    
def CaptchaTextRecognition(captureRegion):
    screenshot = pyautogui.screenshot(region=captureRegion) #Take a screenshot of the specified captureRegion

    # Save the screenshot
    imageFilePath = 'C:/Users/Mike/Documents/Tarkov/Screenshots/screenshot.png'
    screenshot.save(imageFilePath)
    #print(f"Screenshot saved to: {imageFilePath}")
    
    image = cv2.imread(imageFilePath)

    # Use Tesseract to do OCR on the image
    customConfig = r'--oem 3 --psm 6 tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789)(-. tessedit_char_blacklist=@{}'
    text = pytesseract.image_to_string(image, config=customConfig)
    text = text.replace('|', '')  # Remove character
    text = text.replace('{', '')  # Remove character
    text = text.replace('}', '')  # Remove character
    text = text.replace('"', '')  # Remove character
    text = text.replace('@', '0') # Replace @ with 0. It thinks zeros are @.
    text = text.strip()
    if (text[:3] == "WD-"): #Hardcoded fix for WD-40. Will only work for the small WD-40, not the large one.
        text = "WD-40 (100ml)"
    print("Captcha test:" + text)
    return text

def CheckForCaptcha():
    securityCheckPosition = pyautogui.locateOnScreen("Img/SecurityCheck.png", confidence=0.6)
    if (securityCheckPosition is None):
        print("There is no captcha")
        return
    
    # CANT FIND THE IMAGE FOR SOME REASON???
    first_region = pyautogui.locateOnScreen("Img/ConfirmNotABot.png", confidence=0.6)
    if first_region:
        #DrawRedBox(first_region)

        # Define the second region directly below the first one
        captchaTextRegion = (
            first_region.left,                      # Same left X position
            first_region.top + first_region.height, # Directly below the first region
            first_region.width,                     # Same width and the first region
            26                                      # Height
        )        
        #DrawRedBox(captchaTextRegion)
        captchaText = CaptchaTextRecognition(captchaTextRegion)
        print("captchaText: " + captchaText)
        ClickAllInstances(captchaText, CaptchaImageRegion)
        
        #ClickImage("ConfirmBtn", 0.1)
        pyautogui.write("y") # Same thing as clicking the confirm button. 
        return captchaTextRegion
    else:
        print("ConfirmNotABot image not found on the screen.")
        return None

def ClickAllInstances(imageName, theRegion=None, min_distance=60):
    # Locate all instances of the image, with confidence level
    locations = list(pyautogui.locateAllOnScreen(f"Img/{imageName}.png", region=theRegion, confidence=0.9))

    if not locations:
        print(f"No instances of {imageName} found.")
        return

    # List to store filtered locations (no duplicates)
    filtered_locations = []
    for loc in locations:
        # Get the center of the current location
        center = pyautogui.center(loc)

        # Check if the current location is too close to any previously added locations
        too_close = False
        for filtered_loc in filtered_locations:
            if abs(center[0] - filtered_loc[0]) < min_distance and abs(center[1] - filtered_loc[1]) < min_distance:
                too_close = True
                break

        if not too_close:
            filtered_locations.append(center)

    # Click on each filtered location
    for center in filtered_locations:
        pyautogui.moveTo(center)
        pyautogui.click()
        time.sleep(0.1)  # Optional delay between clicks

    print(f"Clicked on {len(filtered_locations)} instances of {imageName}")   

def BuyFromFence():
    itemsToBuy = [
        { "name": "Esmarch tourniquet", "filter": "AllFilterBtn", "minSellPrice": 4262, "fenceCost": 2496 },
        { "name": "Lower half-mask", "filter": "ClothingFilterBtn", "minSellPrice": 6497, "fenceCost": 3399 },
        { "name": "BOSS cap", "filter": "ClothingFilterBtn", "minSellPrice": 4262, "fenceCost": 10859 },
        #{ "name": "Aseptic bandage", "filter": "AllFilterBtn", "minSellPrice": 2147, "fenceCost": 1893} # Only 142 ruble profit. 
    ]

    MustClickImage("TradersTab")
    MustClickImage("FenceIcon")
    ClickImage("BuyBtn") #Makes sure the Buy tab is selected instead of the Sell tab.

    while not stashFull:
        checkRubleBalance()
        for item in itemsToBuy:
            BuyItemFromFence(item['name'], filterName=item["filter"])
            
def BuyItemFromFence(itemName, quantity=50, filterName="AllFilterBtn"):
    ClickImage(filterName, 0.1, traderStoreRegion) #Apply a filter if specified. 
    CheckForCaptcha()

    print("Attempting to buy " + itemName)
    if ClickImage(itemName, 0.1, traderStoreRegion): # Clicks on the item I want to buy. 
        ClickImage("ItemQuantityBtn", 0.1) # Click on the 1 before I start typing in the quanity. Required when I select and item and then select it again later. 
        pyautogui.write(str(quantity))
        ClickImage("DealBtn", 0.1)
        time.sleep(1) # Wait for any popup messages to appear. 

        if (ClickImage("ItemAlreadySold", 2.5)): #Needs to be a high wait time. 
            print("Item already sold")
            ClickImage("OKBtn", 0.1)
            ClickImage("RefreshStore", 0.5)

        elif (ClickImage("NotEnoughSpace", 1)):
            print("Stash is full")
            ClickImage("OKBtn", 0.1)
            global stashFull; stashFull = True
            return
        
        elif (ClickImage("PartialPurchase", 1)):
            print("Partial purchase successful")
            ClickImage("OKBtn", 0.1)
            CheckForCaptcha()
            ClickImage("RefreshStore", 0.1)

        else:
            print("Purchase successful")
            CheckForCaptcha()
    else:
        ClickImage("RefreshStore", 0.1)

def checkRubleBalance():
    # My ruble balance is located in different locations depending on which tab is selected. 
    characterTabRubleRegion = (1620, 45, 145, 25)
    traderTabRubleRegion = (1360, 105, 120, 20)
    fleeMarketRubleRegion = (1475, 70, 125, 20)

    myRublesStr = None
    while myRublesStr is None:    
        if (FindImageOnScreen("CharacterTabSelected")) : rubleRegion = characterTabRubleRegion
        if (FindImageOnScreen("TraderTabSelected")) : rubleRegion = traderTabRubleRegion
        if (FindImageOnScreen("FleaMarketTabSelected")) : rubleRegion = fleeMarketRubleRegion
        #DrawRedBox(rubleRegion)
        myRublesStr = ImageRecognition(rubleRegion)

    # Format as currency without decimal places and add the ruble symbol
    myRublesInt = int(float(myRublesStr))
    formattedNum = f"₽{myRublesInt:,}"
    print(f"My Rubles: {formattedNum}")

    if (int(myRublesStr) < 500000): collectRublesFromRagman()


def collectRublesFromRagman():
    ClickImage("MessengerTab")
    time.sleep(2)                       # Wait for the msg popup to appear.
    ClickImage("RagmanMsgSelected")     # Don't know which image is going to be visible so we check both.
    ClickImage("RagmanMsgNotSelected")  # Don't know which image is going to be visible so we check both.
    ClickImage("ReceiveAllBtn1")        # First click is to display my money to collect. 
    MustClickImage("ReceiveAllBtn2")    # Second click is to actaully collect the money.
    time.sleep(5)                       # The more money I have, the longer I need to wait. 
    MustClickImage("AcceptBtn")         # Closes the collection window.
    return


def SellItemOnFlee(itemFileName, sellPrice):
    MustClickImage("FleeMarketTab")
    MustClickImage("AddOfferBtn")
    MustClickImage("AutoSelectSimilarBtn")
    ScrollToClick(itemFileName, 1, fleeSellingRegion)
    time.sleep(2)
    ClickImage("RubleSellPriceTextBox", 3)
    time.sleep(1)
    pyautogui.write(str(sellPrice))
    ClickImage("PlaceOfferBtn", 3)
    ClickImage("MainMenuTab", 2)


#Main Loop
if __name__ == "__main__":
    
    # Code that only runs when packaged (i.e., when running as an executable)
    if getattr(sys, 'frozen', False): messagebox.showinfo("Information", "To stop the progam, move your cursor to the  top left of the screen.\nProgram will start when you press OK.")
    
    CheckForCaptcha()
    while False: #Used to test the position of stuff on my screen. Update it to True to use it. 
        x, y = pyautogui.position()
        print(f"Current cursor position: ({x}, {y})")
        #CheckForCaptcha()
        #DrawRedBox(CaptchaImageRegion)

    screenRegion = GetMonitorRegion()

    while True:
        #Setup by clicking the main menu first if not already on it, then clicking the character tab. 
        ClickImage("MainMenuTab", 2)
        ClickImage("CharacterTab", 2)
        
        

        BuyFromFence()
        
        
        SellItemOnFlee("Esmarch tourniquet", 4262)
        #SellItemOnFlee("Aseptic bandage", 2149)
        #SellItemOnFlee("Lower half-mask", 7497)
        stashFull = False

print('Program stopped')

# Code that only runs when packaged (i.e., when running as an executable)
if getattr(sys, 'frozen', False): messagebox.showinfo("Information", "Program stopped!")


