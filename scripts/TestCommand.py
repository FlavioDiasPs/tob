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

import bots.lunarush as luna
from helpers.tober import Target, Area
from prodict import Prodict

# time.sleep(3)
# asyncio.run(tob.scroll(updown=-33, repeats=3))

win = pyautogui.getWindowsWithTitle('tob_bombcrypto')[0]
print(win)

# game_area = Area(-8, -8, 812 , 500)
# win.resizeTo(game_area.width, game_area.height)
# win.moveTo(game_area.left, game_area.top)

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