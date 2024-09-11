import pyautogui
import time
import keyboard

while False:
    x, y = pyautogui.position()
    print(f"Current cursor position: ({x}, {y})")

count = 0
search_region = (1700,150,200,100) #First Purchase Button
#search_region = (1700,220,200,200) #Second or third Purchase Button
#pyautogui.click(1248, 1063) #Clicks the Flee Market Button

while True: 
    # Find the location of the image on the screen
    print("Start Looking")
    purchaseImageLocation = pyautogui.locateOnScreen('img/purchase.png', region = search_region, confidence=0.5)
    print("Stop Looking")
    if purchaseImageLocation is not None:
        # Click on the center of the image
        image_center = pyautogui.center(purchaseImageLocation)
        pyautogui.click(image_center)
        
        # Simulate a 'y' press on the keyboard
        pyautogui.press('y')
        print("Pressing y")
        break
        
    else:
        print('Image not found on the screen ' + str(count))
        count = count + 1
        pyautogui.click(1248, 1063) #Clicks the Flee Market Button
        pyautogui.click(1248, 1063) #Clicks the Flee Market Button
        
        #outOfStockImageLocation = None
        #while outOfStockImageLocation is not None:
        #    outOfStockImageLocation = pyautogui.locateOnScreen('img/OutOfStock.png', region = search_region, confidence=0.5)
        #if purchaseImageLocation is not None:
        
        time.sleep(0.8) #Allows the screen to load

    # Check if the user has pressed the 'q' key to quit the program
    if keyboard.is_pressed('q'):
        print('Quitting the program...')
        break

print('Program stopped')