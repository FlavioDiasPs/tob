import asyncio
import cv2
import yaml
import pyautogui
import helpers.tober as tob
import helpers.metamask as metamask

from helpers.printfier import Printer
from helpers.tober import Target, Area
from datetime import datetime
from prodict import Prodict
from os.path import exists


game_area = Area(-8, -8, 800, 630)

btn_back_img = Target(cv2.imread('templates/bombcrypto/btn_back.png'), game_area)
btn_heroes_img = Target(cv2.imread('templates/bombcrypto/btn_heroes.png'), game_area)
btn_treasure_hunt_img = Target(cv2.imread('templates/bombcrypto/btn_treasure_hunt.png'), game_area)
btn_go_work_img = Target(cv2.imread('templates/bombcrypto/btn_go_work.png'), game_area)
btn_x_img = Target(cv2.imread('templates/bombcrypto/btn_x.png'), game_area)
btn_connect_wallet_img = Target(cv2.imread('templates/bombcrypto/btn_connect_wallet.png'), game_area)
btn_connect_metamask_img = Target(cv2.imread('templates/bombcrypto/btn_connect_metamask.png'), game_area)
btn_home_img = Target(cv2.imread('templates/bombcrypto/btn_home.png'), game_area)
green_bar_img = Target(cv2.imread('templates/bombcrypto/green_bar.png'), game_area)
text_error_img = Target(cv2.imread('templates/bombcrypto/text_error.png'), game_area)
btn_bau_img = Target(cv2.imread('templates/bombcrypto/btn_bau.png'), game_area)
bomb_crypto_unavailable_img = Target(cv2.imread('templates/bombcrypto/bomb_crypto_unavailable.png'), game_area)
bomb_didnt_load_img = Target(cv2.imread('templates/bombcrypto/bomb_didnt_load.png'), game_area)
loading_img = Target(cv2.imread('templates/bombcrypto/loading.png'), game_area)
cant_be_reached_img = Target(cv2.imread('templates/chrome/cant_be_reached.png'), game_area)
user_login_img = Target(cv2.imread('templates/bombcrypto/user_login_img.png'), game_area)
pass_login_img = Target(cv2.imread('templates/bombcrypto/pass_login_img.png'), game_area)
btn_login_img = Target(cv2.imread('templates/bombcrypto/btn_login_img.png'), game_area)


class BombBotError(Exception):
    """Raised when BombCrypto shows an error"""
    pass


p = Printer(bot_name='BombCrypto')

async def run_bot(next_action: Prodict):

    p.title('Starting BombCrypto')
    win = next_action.window

    try:
        area = Area(win.left, win.top, win.width, win.height)
        win.resizeTo(game_area.width, game_area.height)
        win.moveTo(game_area.left, game_area.top)
        win.activate()
    
        await handle_error_message()
        await check_load_screen()
        await get_game_ready(win)
        await handle_error_message()

        now = get_now()  
        next_action = adjust_next_action(next_action)          
        send_heroes_interval_sec = next_action.config.intervals.send_heroes_to_work_sec
        send_heroes_schedule_diff = now - next_action.schedules.send_heroes_to_work

        refresh_heroes_interval_sec = next_action.config.intervals.refresh_heroes_positions_sec
        refresh_heroes_schedule_diff = now - next_action.schedules.refresh_heroes_positions

        if send_heroes_schedule_diff > 0:
            await send_heroes_to_work()
            next_action.schedules.send_heroes_to_work = get_now() + send_heroes_interval_sec
            next_action.schedules.refresh_heroes_positions = get_now() + refresh_heroes_interval_sec

        elif refresh_heroes_schedule_diff > 0:
            await refresh_heroes()
            next_action.schedules.refresh_heroes_positions = get_now() + refresh_heroes_interval_sec

        await handle_error_message()

    finally:
        win.moveTo(area.left, area.top)
        win.resizeTo(area.width, area.height) 

    return next_action


def get_now():
    return datetime.timestamp(datetime.now())


def adjust_next_action(next_action: Prodict):
    if 'send_heroes_to_work' not in next_action.schedules:
        next_action.schedules.send_heroes_to_work = 0
        next_action.schedules.refresh_heroes_positions = 0

    return next_action


async def check_load_screen():

    attempts = 0
    attempts_max = 100
    while (attempts < attempts_max):
        if (tob.verify_target_exists(loading_img)):
            await handle_error_message()
            await asyncio.sleep(0.1)
            attempts += 1
        else:
            return

    await tob.refresh_page()


async def handle_error_message():

    if tob.verify_target_exists(text_error_img):
        p.info('Handling error message text_error_img')
        await tob.refresh_page()
        raise BombBotError(" ** BombCryp to displayed an error message: text_error_img. Restarting...")

    elif tob.verify_target_exists(bomb_crypto_unavailable_img):
        p.info('Handling error message bomb_crypto_unavailable')
        await tob.refresh_page()
        raise BombBotError(" ** BombCrypto displayed an error message: bomb_crypto_unavailable. Restarting...")

    elif tob.safe_retry(tob.verify_target_exists, [bomb_didnt_load_img], expected_result=False):
        p.info('Handling error message bomb_didnt_load')
        await tob.refresh_page()
        raise BombBotError(" ** BombCrypto displayed an error message: bomb_didnt_load. Restarting...")

    elif tob.safe_retry(tob.verify_target_exists, [cant_be_reached_img], max_attempts=3, expected_result=True):
        await tob.click_target_center_async(cant_be_reached_img, sleep_after_click_sec=2)
        raise BombBotError("Site cant be reached, probably there is a internet problem...")


async def get_game_ready(window):

    if is_connected() == False:
        return await connect_wallet(window)
    return True


def is_connected():
    ''' Check if you are connected to your wallet or have been disconnected from any errors '''

    p.info('Checking if you are connected')

    if tob.safe_retry(tob.verify_target_exists, params=[btn_bau_img], expected_result=True, 
                                                attempt_delay=0.1, max_attempts=10):
        p.info('You are connected')
        return True
    else:
        p.info('You are not connected')
        return False


async def connect_wallet(window):

    try:
        p.info('Connecting wallet')
        await tob.click_target_center_async(target=btn_connect_wallet_img, expected_result=True, sleep_after_click_sec=1)
        await handle_error_message()
        
        scholar_path = 'bomb_scholar.yaml'
        file_exists = exists(scholar_path)

        if file_exists:
            all_accounts = Prodict(yaml.safe_load(open(scholar_path, 'r')))

        if file_exists and window.title in all_accounts:
            user = str(all_accounts[window.title]['user'])
            password = str(all_accounts[window.title]['pass'])

            await tob.safe_click_target_center_async(user_login_img,  x_offset=30)
            pyautogui.write(user)

            await tob.safe_click_target_center_async(pass_login_img,  x_offset=30)
            pyautogui.write(password)
            
            await tob.safe_click_target_center_async(btn_login_img)

        else:

            p.info('Connecting metamask')
            await tob.click_target_center_async(target=btn_connect_metamask_img, expected_result=True, sleep_after_click_sec=1)
            await handle_error_message()

            p.info('Signing metamask')
            await metamask.signin()
            await check_game_loaded()

    except:
        await tob.refresh_page()
        raise


async def check_game_loaded():

    attempts = 0
    max_attempts=100

    p.info('Waiting loading...')
    while(attempts <= max_attempts):
        attempts += 1

        await handle_error_message()
        if tob.verify_target_exists(btn_treasure_hunt_img): break
        await asyncio.sleep(0.1)

    if attempts > max_attempts:
        raise BombBotError("Couldn't load the game")
    
    


async def send_heroes_to_work():
    ''' Send heroes to work '''

    p.info('Putting heroes to work')

    await tob.safe_click_target_center_async(btn_x_img, max_attempts=5)
    await tob.safe_click_target_center_async(btn_back_img, max_attempts=5)
    await handle_error_message()
    
    custom_error = "Couldn't find heroes_img. Starting from the beginning"
    await tob.click_target_center_async(target=btn_heroes_img, expected_result=True, custom_error=custom_error)
    await handle_error_message()

    await tob.move_mouse_target_center_async(btn_home_img)

    heroes_go_work = 0
    scrolls = 0
    while scrolls <= 2:

        heroes_go_work += click_go_work()

        if scrolls != 2:
            await tob.scroll(-1, 20, sleep_after_scroll=0)

        scrolls += 1

    if heroes_go_work != 0:
        p.info('Heroes are working')
    else:
        p.info('No hero have enough stamina')

    p.info('Getting back to Treasure Hunt')

    await tob.safe_click_target_center_async(btn_x_img)
    await asyncio.sleep(2)

    while(tob.verify_target_exists(btn_treasure_hunt_img)):
        p.info('Entering treasure hunt')
        await tob.safe_click_target_center_async(btn_treasure_hunt_img)
        await asyncio.sleep(2)


def click_go_work():
    ''' Activate heroes that are being displayed on the monitor with green stamina '''

    x_offset = 100
    not_working_green_bars = []

    green_bars = tob.locate_target(green_bar_img)

    for bar in green_bars:
        not_working_green_bars.append(bar)

    if len(not_working_green_bars) > 0:
        for (x, y, w, h) in not_working_green_bars:

            center_x = w / 2
            center_y = h / 2

            x = x + x_offset + center_x
            y = y + center_y

            pyautogui.moveTo(x, y, 0.2)
            pyautogui.click()

    return len(not_working_green_bars)


async def refresh_heroes():
    ''' Update heroes' position by preventing them from jamming, exiting the map, or the user being kicked out of absence in the game '''

    p.info('Refreshing heroes positions')

    await handle_error_message()
    await tob.safe_click_target_center_async(btn_back_img)    

    await handle_error_message()

    while(tob.verify_target_exists(btn_treasure_hunt_img)):
        await tob.safe_click_target_center_async(btn_treasure_hunt_img)
        await asyncio.sleep(2)   