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
import bots.cryptopiece as piece
from helpers.tober import Target, Area
from prodict import Prodict

# time.sleep(3)
# asyncio.run(tob.scroll(updown=-33, repeats=3))


# while(True):
    
    # win = pyautogui.getWindowsWithTitle('tob_lunarush')[0]
    # print(win)

    # win.minimize()
    # time.sleep(2)
    # win.restore()
    # time.sleep(2)





    # print(tob.verify_target_exists(piece.btn_battlefield_criminal_img))
    # print('-----')
    # time.sleep(0.5)


# win = pyautogui.getWindowsWithTitle('tob_spacecrypto')[0]
# print(win)

# game_area = Area(-8, -8, 812 , 500)
# win.resizeTo(game_area.width, game_area.height)
# win.moveTo(game_area.left, game_area.top)

while(True):
    print(pyautogui.mouseinfo.position())
    time.sleep(0.5)



# asyncio.run(tob.hold_move_async(270, 300, 290, 125, max_x_precision_offset=2, min_move_duration=0.5, max_move_duration=0.8))

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