import asyncio
from json import tool
import random
from time import time
from typing import List
import helpers.tober as tob
import pyautogui
import time
import cv2
from mss import mss, tools
import numpy as np

from helpers.tober import Target, Area


time.sleep(3)
asyncio.run(tob.scroll(updown=-380, repeats=3))
time.sleep(1)
asyncio.run(tob.scroll(updown=-380, repeats=3))



# while(True):
#     print(pyautogui.mouseinfo.position())
#     time.sleep(0.5)

# search_area = tob.Area(50, 520, 220, 100)

# with mss() as screen:
#     monitor = screen.monitors[1]

#     left = monitor['left'] + search_area.left
#     top = monitor['top'] + search_area.top
#     width = left + search_area.width
#     height = top + search_area.height

#     shoot_area = (left, top, width, height)
#     grabed = screen.grab(shoot_area)

#     tools.to_png(grabed.rgb, grabed.size, level=6, output='out.png')

#     screenshot = np.array(grabed)


# import pyautogui
# import math

# # Radius 
# R = 400
# # measuring screen size
# (x,y) = pyautogui.size()
# # locating center of the screen
# (X,Y) = pyautogui.position(x/2,y/2)
# # offsetting by radius 
# pyautogui.moveTo(X+R,Y)

# for i in range(360):
#     # setting pace with a modulus 
#     if i%6==0:
#        pyautogui.moveTo(X+R*math.cos(math.radians(i)),Y+R*math.sin(math.radians(i)))