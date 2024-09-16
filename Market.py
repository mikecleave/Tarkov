"""
SET UP:
1. Must set your monitor resolution to 1920 x 1080.

*** Discuss wishlist setup ***

"""


"""
*** To DO ***
1. Add a msg  box that the program has stopped when the user moves their cursor to the top left of the screen. 
2. When I buy an item from fence, I need to keep buying it until its out of stock before switching to the next item. 
3. If I drop below a specific amount of money, I need to accept the money from Ragman.
4. Buy barter items low and resell them high. Ex: buy wires for 10k or less and sell hem for 13k.

1. Esmarch improvments:
    - If I am only buying esmarches, I should not bother refreshing the stock if there is 1 image on the screen. Will allow me to buy them faster. 
"""


"""
*** HOW TO PACKAGE ***
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
fleeSellingRegion = (0, 0, 650, 1000) #Your flee selling windown needs to be in the top left corner.
#CaptchaTextRegion = (777, 365, 372, 26)
CaptchaImageRegion = (684, 230, 546, 813)
fleaOfferNumRegion = (420, 46, 33, 17)
wishListRowSize = (70, 150, 300, 30)
itemRowSize = (1700, 145, 130, 70)
fleaPriceRegion = (1340, 145, 140, 70)

# IF THIS LIST IS NOT IN THE SAME ORDER AS MY IN GAME WISH LIST, IT WILL BUY THE WRONG ROW ITEM. 
wishListItems = [
    { "name": "AK-101 Mag", "rowToPurchase": 1, "rowWithMinCost": 2, "minSellPrice": 3997, "maxSellPrice": 4997,  "traderCost": 1808 },
    { "name": "Ammo Case", "rowToPurchase": 1, "rowWithMinCost": 3, "minSellPrice": 189897, "maxSellPrice": 199897,"traderCost": 162552 },
    { "name": "F-1 hand grenade", "rowToPurchase": 2, "rowWithMinCost": 5,"minSellPrice": 14997, "maxSellPrice": 15997,"traderCost": 9156 },
    { "name": "PACA", "rowToPurchase": 1, "rowWithMinCost": 2, "minSellPrice": 29151, "maxSellPrice": 29151, "traderCost": 10000 },
    { "name": "Rye crutons", "rowToPurchase": 2, "rowWithMinCost": 3, "minSellPrice": 29997, "maxSellPrice": 29997, "traderCost": 10000 },
]

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

def Click(coordinates, delay=0.1):
    x, y = coordinates
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
    time.sleep(delay)  # Add delay before trying to find the image
    position = FindImageOnScreen(imageName, region, grayscale=grayscale)
    if position:
        print(f"Found {imageName} at: {position}")
        Click(position)
        return True
    else:
        print(f"{imageName} not found on the screen.")
        return False

def MustClickImage(imageName, delay=1, region=None):
    isSuccessfull = False
    while not isSuccessfull:
        position = FindImageOnScreen(imageName, region)
        if position:
            print(f"Found {imageName} at: {position}")
            Click(position, delay)
            isSuccessfull = True
        else:
            print(f"{imageName} not found on the screen.")

def ScrollToTop():
    print("Scrolling to the top to reset for the next item")
    for i in range(50):
        pyautogui.scroll(5000) #Scroll up - doesn't matter what the number is. Each one will only scroll 1 line

def ScrollDown(rowsToScroll):
    for i in range(rowsToScroll):
        pyautogui.scroll(-5000) #Scroll down - doesn't matter what the number is. Each one will only scroll 1 line

def ScrollToClick(imageName, delay=1, region=None):
    isSuccessfull = False
    scrollCount = 0
    # Scroll until the item is found OR you reach the bottom. 
    while not isSuccessfull and scrollCount < 10:
        position = FindImageOnScreen(imageName, region)
        if position:
            print(f"Found {imageName} at: {position}")

            # Right clicks and filters by the item so we can see what its selling for. 
            pyautogui.rightClick(position)
            ClickImage("FilterByItem", 0.3)

            # Select the item to sell. We do this after filtering by the item since the image looks different when selected. 
            Click(position, delay)
            isSuccessfull = True
            return True
        else:
            print(f"{imageName} not found on the screen. Scrolling down")
            pyautogui.moveTo(region)
            ScrollDown(6)
            scrollCount = scrollCount + 1

    if isSuccessfull == False:
        return False   

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
    
    # Load the captured screenshot image
    image = cv2.imread(imageFilePath)

    # Use Tesseract to do OCR on the image
    customConfig = r'--oem 3 --psm 6 tessedit_char_whitelist=0123456789₽'
    number = pytesseract.image_to_string(image, config=customConfig)
    
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
        { "name": "Esmarch tourniquet", "filter": "MedFilterBtn", "minSellPrice": 4262, "fenceCost": 2496 },
        { "name": "Lower half-mask", "filter": "ClothingFilterBtn", "minSellPrice": 6497, "fenceCost": 3399 },
        { "name": "Anti-fragmentation glasses", "filter": "ClothingFilterBtn", "minSellPrice": 4262, "fenceCost": 2836 },
        #{ "name": "BOSS cap", "filter": "ClothingFilterBtn", "minSellPrice": 19997, "fenceCost": 10859 },
        #{ "name": "Aseptic bandage", "filter": "MedFilterBtn", "minSellPrice": 2147, "fenceCost": 1893} # Only 142 ruble profit. 
    ]

    MustClickImage("TradersTab")
    MustClickImage("FenceIcon")
    ClickImage("BuyBtn") #Makes sure the Buy tab is selected instead of the Sell tab.

    while not stashFull:
        #checkRubleBalance() # THIS NEEDS TO BE FIXED. 
        for item in itemsToBuy:
            if stashFull: return
            BuyItemFromFence(item['name'], filterName=item["filter"])
            
def BuyItemFromFence(itemName, quantity=50, filterName="AllFilterBtn"):
    ClickImage(filterName, 0.1, traderStoreRegion) #Apply a filter if specified. 
    CheckForCaptcha()
    ClickImage("OKBtn", 0.1) # Incase there is a popup that was missed. 

    print("Attempting to buy " + itemName)
    if ClickImage(itemName, 0.1, traderStoreRegion): # Clicks on the item I want to buy. 
        ClickImage("ItemQuantityBtn", 0.1) # Click on the 1 before I start typing in the quanity. Required when I select and item and then select it again later. 
        pyautogui.write(str(quantity))
        ClickImage("DealBtn", 0.1)
        time.sleep(1) # Wait for any popup messages to appear. 

        # Merge all these IF statements into one. 
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

def SellFromFence():
    return

def CheckRubleBalance():
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

    if (int(myRublesStr) < 100000): CollectRublesFromRagman()

def CollectRublesFromRagman():
    ClickImage("MessengerTab")
    time.sleep(2)                       # Wait for the msg popup to appear.
    ClickImage("RagmanMsgSelected")     # Don't know which image is going to be visible so we check both.
    ClickImage("RagmanMsgNotSelected")  # Don't know which image is going to be visible so we check both.
    ClickImage("ReceiveAllBtn1")        # First click is to display my money to collect. 
    MustClickImage("ReceiveAllBtn2")    # Second click is to actaully collect the money.
    time.sleep(5)                       # The more money I have, the longer I need to wait. 
    MustClickImage("AcceptBtn")         # Closes the collection window.
    return

def GetRegionCenters(firstRegion, regionNum):
    left, top, width, height = firstRegion

    for i in range(regionNum):
        # Calculate the center x and y for the current region
        center_x = left + width / 2
        center_y = top + height / 2
        
        # Add the center coordinates to the list
        regionCoordinates = (center_x, center_y)
        
        # Update the top for the next region (since they cascade vertically with no space)
        top += height  # Move the top of the next region down by the height of the current region
    return regionCoordinates

def GetPriceRegion(firstRegion, regionNum):
    left, top, width, height = firstRegion
    
    for i in range(1, regionNum):                
        # Update the top for the next region (since they cascade vertically with no space)
        top += height  # Move the top of the next region down by the height of the current region
    return (left, top, width, height)

def BuyFromWishList():
    # Loop through each item on the wishlist. Need to specify which row to the item is in that we want to buy. 
    ClickImage("OKBtn") #Just incase there is a popup overlay still from buying from fence. 
    ClickImage("FleaMarketTab")
    ClickImage("BrowseBtn", 0.5)
    ClickImage("BarterItemsGroup", 1)  #Makes sure an item from my wishlist isn't already selected. 
    ClickImage("WishListBtn", 1)

    count = 1
    for item in wishListItems:
        print("Attempting to buy: " + item['name'])       
        itemCenter = GetRegionCenters(wishListRowSize, count)
        Click(itemCenter, 1.5) # Clicks the item in the wishlist
        Click(GetRegionCenters(itemRowSize, item["rowToPurchase"]), 0.5) # Clicks the PURCHASE button. 
        ClickImage("AllBtn", 0.5)
        ClickImage("AllBarterBtn", 0.5)
        if ClickImage("InsufficientBarterItemsIcon"):
            print("Insufficient Barter Items")
            pyautogui.press('esc')
        else:
            time.sleep(0.5) #This can prob be shorter.
            pyautogui.write("y")
        ClickImage("OKBtn") #Incase you run our of storage space. 
        count = count+1

def SellFromWishList():
    for item in wishListItems:
        SellItemOnFlee(item)

def SellItemOnFlee(item, sellPrice=None):
    MustClickImage("MainMenuTab")
    print("Attempting to sell: " + item['name'])
    ClickImage("FleaMarketTab")

    # If there is an availible sell slot
    if ClickImage("AddOfferBtn", 3): # Needs a long wait. 
        ClickImage("AutoSelectUnChecked", 2)

        if ScrollToClick(item['name'], 1, fleeSellingRegion):
            if sellPrice == None: # If I am selling an item from my wishlist. 
                sellPrice = GetItemSellPrice(item)
                if sellPrice == False: # This item is already for sale, or the image recognition could not determin the min flea price. 
                    return False
                ClickImage("RubleSellPriceTextBox", 3)
                time.sleep(1)            
                pyautogui.write(str(sellPrice))
            else: # Used when calling the function directly such as selling esmarches. 
                pyautogui.write(str(sellPrice))
            ClickImage("PlaceOfferBtn", 0.5)
            return True
        else:
            print("Could not find " + item['name'] + " to sell")    
            return False
    else:
        print("NO MORE SELL SLOTS AVAILIBLE")
        return False
    
def GetItemSellPrice(item):
    # Checks if the item is already for sale. If  it is, don't sell another. 
    if FindImageOnScreen("RemoveFromFleaBtn"):
        print(item["name"] + " is already for sale")
        return False

    # Used to specify the exact sell price every time. 
    elif item["minSellPrice"] == item['maxSellPrice']:
        return item["minSellPrice"]
    
    # Check the cheapest value someone else is selling the item for and under cut them by 3 rubles. 
    region = GetPriceRegion(fleaPriceRegion, item["rowWithMinCost"])
    strPrice = ImageRecognition(region)
    intPrice = int(strPrice)
    print("Min price on the flea is: " + strPrice)
    if strPrice == "":
        print("Something went wrong identifying the min flea price")
        return False
    elif intPrice < int(item["minSellPrice"]):
        print(f"Current price ({strPrice}) is lower than what I am willing to sell at ({item['minSellPrice']})")
        return False
    return intPrice-3 # Sell the item for 3 ruble less then the minimum offer.  


# THIS DONES'T WORK YET. WE ARE GOING TO ASSUME WE ALWAYS HAVE AT LEAST 1 SELL SLOT AVAILIBLE. 
def getAvailibleSellSlots():
    #text = ImageRecognition(fleaOfferNumRegion)
    #print(text)
    numSellSlots = 1
    return numSellSlots

#Main Loop
if __name__ == "__main__":
    
    # Code that only runs when packaged (i.e., when running as an executable)
    if getattr(sys, 'frozen', False): messagebox.showinfo("Information", "To stop the progam, move your cursor to the  top left of the screen.\nProgram will start when you press OK.")
    
    CheckForCaptcha()

    while False: #Used to test the position of stuff on my screen. Update it to True to use it. 
        x, y = pyautogui.position()
        print(f"Current cursor position: ({x}, {y})")
        #BuyFromWishList()
        #SellFromWishList()
        #CheckForCaptcha()
        #DrawRedBox(fleaPriceRegion)

    screenRegion = GetMonitorRegion()

    while True:
        #Setup by clicking the main menu first if not already on it, then clicking the character tab. 
        ClickImage("MainMenuTab", 2)
        ClickImage("CharacterTab", 2)
        
        BuyFromWishList()
        SellFromWishList()
        
        CollectRublesFromRagman()

        BuyFromFence()        
        #SellFromFence()

        SellItemOnFlee("Esmarch tourniquet", 4262, 1)
        SellItemOnFlee("Lower half-mask", 7997, 1)
        #SellItemOnFlee("Aseptic bandage", 2149)
        #SellItemOnFlee("Lower half-mask", 7497)
        stashFull = False

print('Program stopped')

# Code that only runs when packaged (i.e., when running as an executable)
if getattr(sys, 'frozen', False): messagebox.showinfo("Information", "Program stopped!")


