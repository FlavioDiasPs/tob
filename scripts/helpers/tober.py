import asyncio
from uuid import uuid4
import pyautogui
import time
import numpy as np
import pygetwindow
import random

from cv2 import cv2
from mss import mss
from typing import Any,  List


class Area:
    left = 0
    top = 0
    width = 0
    height = 0

    def __init__(self,  left = 0, top = 0, width = 0, height = 0):
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class Target:
    img: Any = None
    area: Area = Area()

    def __init__(self, img, area=Area()):
        self.img = img
        self.area = area



# window
async def refresh_page():
    pyautogui.hotkey('ctrl', 'f5') 
    pyautogui.press('enter')
    await asyncio.sleep(4)
  

async def scroll(updown = -1, repeats = 20, sleep_after_scroll = 0.3):
    ''' Scroll the mouse '''
    
    for i in range(0, repeats):
        pyautogui.scroll(clicks=updown)

    await asyncio.sleep(sleep_after_scroll)


def screenshot(search_area: Area()):
    
    with mss() as screen:
        monitor = screen.monitors[1]

        left = monitor['left'] + search_area.left
        top = monitor['top'] + search_area.top
        width = left + search_area.width
        height = top + search_area.height

        if width == 0:
            width = monitor['width']

        if height == 0:
            height = monitor['height']

        shoot_area = (left, top, width, height)
        grabed = screen.grab(shoot_area)
        screenshot = np.array(grabed)   

        # from mss import tools
        # tools.to_png(grabed.rgb, grabed.size, level=6, output=f'{uuid4()}_out.png')

        return screenshot[:, :, :3]



# targets
def click(click_amount: int = 1):
    click_count = 0
    
    while(click_count < click_amount):
        click_count += 1
        pyautogui.click()
        time.sleep(0.08)

def move(x, y, duration=random.uniform(0.1, 0.3)):
    pyautogui.moveTo(x, y, duration, pyautogui.easeInBounce)


async def find_targets_centers_async(target: Target, max_attempts=10, attempt_delay=0.2, 
                                    confidence=0.9):
    attempts = 0
    matches = []

    while len(matches) <= 0 and attempts < max_attempts:
        matches = locate_target(target, confidence)
        await asyncio.sleep(attempt_delay)
        attempts += 1

    else:
        if attempts == max_attempts:
            return []
            
        targets_centers = []
        for (x, y, w, h) in matches:

            relative_center_x = w / 2
            relative_center_y = h / 2

            x = x + relative_center_x
            y = y + relative_center_y

            targets_centers.append((x, y))

    return targets_centers


async def click_location_async(x, y, x_offset = 0, y_offset = 0, 
                min_x_precision_offset = 1, max_x_precision_offset = 10,
                min_y_precision_offset = 1, max_y_precision_offset = 10,
                min_move_duration = 0.1, max_move_duration = 0.2,
                min_click_duration = 0.05, max_click_duration = 0.1,
                sleep_after_click_sec = 0.2):

    rnd_x = x + x_offset + random.uniform(min_x_precision_offset, max_x_precision_offset)
    rnd_y = y + y_offset + random.uniform(min_y_precision_offset, max_y_precision_offset)

    moreless_y = random.randint(-1, 1) 
    moreless_x = random.randint(-1, 1) 
    if moreless_y == 0: moreless_y = 1
    if moreless_x == 0: moreless_x = 1
 
    side_move_x = rnd_x + random.uniform(20, 40) * moreless_x
    side_move_y = rnd_y + random.uniform(20, 40) * moreless_y

    # pyautogui.moveTo(side_move_x, side_move_y, random.uniform(0.2, 0.3), pyautogui.easeInBack)
    pyautogui.moveTo(rnd_x, rnd_y, random.uniform(min_move_duration, max_move_duration), pyautogui.easeOutBounce)
    pyautogui.click(duration=random.uniform(min_click_duration, max_click_duration))

    await asyncio.sleep(sleep_after_click_sec)    


async def hold_move_async(start_x, start_y, end_x, end_y, 
                min_x_precision_offset = 1, max_x_precision_offset = 2,
                min_y_precision_offset = 1, max_y_precision_offset = 2,
                min_move_duration = 0.5, max_move_duration = 0.7,
                sleep_after_click_sec = 0.2):
 
    rnd_x = start_x + random.uniform(min_x_precision_offset, max_x_precision_offset)
    rnd_y = start_y + random.uniform(min_y_precision_offset, max_y_precision_offset)

    rnd_end_x = end_x + random.uniform(min_x_precision_offset, max_x_precision_offset)
    rnd_end_y = end_y + random.uniform(min_y_precision_offset, max_y_precision_offset)

    moreless_y = random.randint(-1, 1) 
    moreless_x = random.randint(-1, 1) 
    if moreless_y == 0: moreless_y = 1
    if moreless_x == 0: moreless_x = 1
 
    side_move_x = rnd_x + random.uniform(20, 40) * moreless_x
    side_move_y = rnd_y + random.uniform(20, 40) * moreless_y

    pyautogui.moveTo(side_move_x, side_move_y, random.uniform(0.2, 0.3), pyautogui.easeInBack)
    
    pyautogui.moveTo(rnd_x, rnd_y, random.uniform(min_move_duration, max_move_duration), pyautogui.easeOutBounce)
    pyautogui.mouseDown()
    
    pyautogui.moveTo(rnd_end_x, rnd_end_y, random.uniform(min_move_duration, max_move_duration), pyautogui.easeOutBounce)
    
    await asyncio.sleep(0.5)
    pyautogui.mouseUp()

    await asyncio.sleep(sleep_after_click_sec)



async def hold_move_release_async(start_x, start_y, end_x, end_y, 
                min_x_precision_offset = 1, max_x_precision_offset = 2,
                min_y_precision_offset = 1, max_y_precision_offset = 2,
                min_move_duration = 0.28, max_move_duration = 0.35,
                sleep_after_click_sec = 0.2):
 
    rnd_x = start_x + random.uniform(min_x_precision_offset, max_x_precision_offset)
    rnd_y = start_y + random.uniform(min_y_precision_offset, max_y_precision_offset)

    rnd_end_x = end_x + random.uniform(min_x_precision_offset, max_x_precision_offset)
    rnd_end_y = end_y + random.uniform(min_y_precision_offset, max_y_precision_offset)

    moreless_y = random.randint(-1, 1) 
    moreless_x = random.randint(-1, 1) 
    if moreless_y == 0: moreless_y = 1
    if moreless_x == 0: moreless_x = 1
 
    pyautogui.moveTo(rnd_x, rnd_y, random.uniform(min_move_duration, max_move_duration))
    pyautogui.mouseDown()
    
    pyautogui.moveTo(rnd_end_x, rnd_end_y, random.uniform(min_move_duration, max_move_duration))
    
    await asyncio.sleep(0.5)
    pyautogui.mouseUp()

    await asyncio.sleep(sleep_after_click_sec)


async def click_all_targets_center_async(target: Target, max_attempts=10, 
                                x_offset = 0, y_offset = 0,
                                min_x_precision_offset = 1, max_x_precision_offset = 10,
                                min_y_precision_offset = 1, max_y_precision_offset = 10,
                                sleep_after_click_sec = 1, confidence=0.9):
    ''' Click on an identified image
        target = template
        max_attemps = maximum attempts to click this template
     '''

    locations = await find_targets_centers_async(target, max_attempts=max_attempts, confidence=confidence)

    if len(locations) <= 0:
        return []
    
    for location in locations:
        x = location[0] + x_offset
        y = location[1] + y_offset
        min_xpo = min_x_precision_offset
        max_xpo = max_x_precision_offset
        min_ypo = min_y_precision_offset
        max_ypo = max_y_precision_offset

        await click_location_async(x=x, y=y, 
                        min_x_precision_offset=min_xpo, max_x_precision_offset=max_xpo,
                        min_y_precision_offset=min_ypo, max_y_precision_offset=max_ypo,
                        sleep_after_click_sec=sleep_after_click_sec)

    return locations
    

async def safe_click_target_center_async(target: Target, max_attempts=10, attempt_delay=0.2,
                                x_offset=0, y_offset=0,
                                min_x_precision_offset = 1, max_x_precision_offset = 7,
                                min_y_precision_offset = 1, max_y_precision_offset = 7,
                                sleep_after_click_sec = 0.2, confidence=0.9):
    ''' Click on an identified image
        target = template
        max_attemps = maximum attempts to click this template
     '''

    locations = await find_targets_centers_async(
            target, max_attempts=max_attempts, attempt_delay=attempt_delay, 
            confidence=confidence
        )
    
    if locations:
        location = locations[0]
        x = location[0]
        y = location[1]
        min_xpo = min_x_precision_offset
        max_xpo = max_x_precision_offset
        min_ypo = min_y_precision_offset
        max_ypo = max_y_precision_offset

        await click_location_async(x=x, y=y, 
                        x_offset=x_offset, y_offset=y_offset,
                        min_x_precision_offset=min_xpo, max_x_precision_offset=max_xpo,
                        min_y_precision_offset=min_ypo, max_y_precision_offset=max_ypo,
                        sleep_after_click_sec=sleep_after_click_sec)
        return True
    else:
        return False


async def move_mouse_target_center_async(target: Target, max_attemps=10, x_offset=0, y_offset=0):
    ''' Click on an identified image
        target = template
        max_attemps = maximum attempts to click this template
     '''

    locations = await find_targets_centers_async(target, max_attemps)
    
    if locations and len(locations) > 0:
        # locations = sorted(locations, key=lambda l: l[1], reverse=False)
        location = locations[0]
        random_x_path = location[0] + x_offset + random.uniform(1, 20)
        random_y_path = location[1] + y_offset + random.uniform(1, 20)

        pyautogui.moveTo(random_x_path, random_y_path, random.uniform(0.1, 0.25), pyautogui.easeInBounce)
        return True
    else:
        return False


async def click_target_center_async(target: Target, max_attempts=20, attempt_delay=0.2, expected_result=True,
                         custom_error: str = "Didn't find target", sleep_after_click_sec=0.5,
                         confidence=0.9):

    result = await safe_click_target_center_async(
        target, max_attempts=max_attempts, attempt_delay=attempt_delay,
        confidence=confidence, sleep_after_click_sec=sleep_after_click_sec
    )

    if result != expected_result:
        raise Exception(custom_error)


def wait_target_appear_disappear(target: Target, max_attempts=99, attempt_delay=0.2, expected_result=True,
                            custom_error: str = "Didn't find target", confidence=0.9):
    
    retry(
        verify_target_exists, [target, confidence], max_attempts=max_attempts, 
                                attempt_delay=attempt_delay, expected_result=expected_result,
                                custom_error=custom_error
        )


def verify_target_exists(target: Target, confidence=0.9):
    ''' Check for an identified template on the monitor
        target = template 
    '''
    try:

        if len(locate_target(target, confidence)) <= 0:
            return False
        else:
            return True

    except:
        return False


def verify_target_ocorrency_amount(target: Target, confidence=0.9):
    ''' Check for an identified template on the monitor
        target = template
    '''
    try:
        
        amount = len(locate_target(target, confidence))
        
        if amount <= 0:
            return 0
        else:
            return amount

    except Exception as e:
        raise e


def locate_target(target: Target, confidence=0.9): 
    img = screenshot(target.area)
    result = cv2.matchTemplate(img, target.img, cv2.TM_CCOEFF_NORMED)

    w = target.img.shape[1]
    h = target.img.shape[0]
    yloc, xloc = np.where(result >= confidence)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x) + target.area.left, int(y) + target.area.top, int(w), int(h)])
        rectangles.append([int(x) + target.area.left, int(y) + target.area.top, int(w), int(h)])

    sorted_rectangles = sorted(rectangles)
    grouped_rectangles, weights = cv2.groupRectangles(sorted_rectangles, 1, 0.2)
  
    return grouped_rectangles




# windows
def activate_window_by_name(window_name):
    windows = pygetwindow.getWindowsWithTitle(window_name)

    if len(windows) > 0:
        windows[0].activate()


def close_windows_by_name(window_name):
    bomb_windows = pygetwindow.getWindowsWithTitle(window_name)

    result = False
    for bomb_window in bomb_windows:
        bomb_window.close()
        result = True

    return result
        


# Assistance
async def retry_async(f, params: List[Any]=None, max_attempts=20, attempt_delay=0.2,
                      expected_result=None, custom_error: str = "Didn't work like expected"):
    attemp_count = 1

    while(attemp_count <= max_attempts):
        attemp_count += 1

        try:
            result = None
            
            if params:
                result = await f(*params)
            else:
                result = await f()

            if expected_result != None:
                if result != expected_result:
                    raise Exception(custom_error)
                else:
                    return result

            else:
                return result

        except Exception as e:

            if(attemp_count > max_attempts):
                raise e

            await asyncio.sleep(attempt_delay)
            print(f' **** Running attempt {attemp_count}/{max_attempts}', end='\r')


def retry(f, params: List[Any]=None, max_attempts=20, attempt_delay=0.2,
          expected_result=None, custom_error: str = "Didn't work like expected"):
    attemp_count = 1

    while(attemp_count <= max_attempts):
        attemp_count += 1

        try:
            result = None
            
            if params:   
                result = f(*params)
            else:
                result = f()
      
            if expected_result != None:
                if result != expected_result:
                    raise Exception(custom_error)
                else:
                    return result
            
            else:
                return result

        except Exception as e:

            if(attemp_count > max_attempts):
                raise e

            time.sleep(attempt_delay)
            print(f' **** Running attempt {attemp_count}/{max_attempts}', end='\r')


def safe_retry(f, params: List[Any]=None, max_attempts=20, attempt_delay=0.1, expected_result=None):
    attemp_count = 1

    while(attemp_count <= max_attempts):
        attemp_count += 1

        try:
            result = None
            
            if params:
                result = f(*params)
            else:
                result = f()

            if expected_result != None:
                if result != expected_result:
                    if(attemp_count > max_attempts):
                        return result
                else:
                    return result
            
            else:
                return result

        except Exception as e:

            if(attemp_count > max_attempts):
                raise e

        time.sleep(attempt_delay)
        print(f' **** Running attempt {attemp_count}/{max_attempts}', end='\r')
   
   
async def safe_retry_async(f, params: List[Any]=None, max_attempts=20, attempt_delay=0.2, expected_result=None):
    attemp_count = 1

    while(attemp_count <= max_attempts):
        attemp_count += 1

        try:
            result = None
            
            if params:
                result = await f(*params)
            else:
                result = await f()

            if expected_result != None:
                if result != expected_result:
                    if(attemp_count > max_attempts):
                        return result
                else:
                    return result

            else:
                return result

        except Exception as e:

            if(attemp_count > max_attempts):
                raise e

        time.sleep(attempt_delay)
        print(f' **** Running attempt {attemp_count}/{max_attempts}', end='\r')


def anyone(f, params: List):
    return any(f(param) for param in params)


def anyone_multi_param(f, params: List):
    return any(f(*param) for param in params)
