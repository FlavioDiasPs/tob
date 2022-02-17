import asyncio
import random
import traceback
import cv2

from datetime import datetime
from prodict import Prodict 

import helpers.tober as tob
import helpers.metamask as metamask

from helpers.printfier import Printer
from helpers.tober import Target, Area

game_area = Area(-8, -8, 570, 445)

btn_connect_wallet_img = Target(cv2.imread('templates/spacecrypto/btn_connect_wallet_img.PNG'), game_area)
loading_unity_img = Target(cv2.imread('templates/spacecrypto/loading_unity_img.PNG'), game_area)
processing_img = Target(cv2.imread('templates/spacecrypto/processing_img.PNG'), game_area)

btn_play_img = Target(cv2.imread('templates/spacecrypto/btn_play_img.png'), game_area)
btn_spaceship_inventory_img = Target(cv2.imread('templates/spacecrypto/btn_spaceship_inventory_img.png'), game_area)
btn_spaceship_fight_img = Target(cv2.imread('templates/spacecrypto/btn_spaceship_fight_img.png'), game_area)
btn_fight_boss_img = Target(cv2.imread('templates/spacecrypto/btn_fight_boss_img.png'), Area(360, 320, 190, 90))
btn_surrender_img = Target(cv2.imread('templates/spacecrypto/btn_surrender_img.png'), game_area)

btn_surrender_confirm_img = Target(cv2.imread('templates/spacecrypto/btn_surrender_confirm_img.png'), game_area)
btn_victory_confirm_img = Target(cv2.imread('templates/spacecrypto/btn_victory_confirm_img.png'), game_area)
btn_loss_confirm_img = Target(cv2.imread('templates/spacecrypto/btn_loss_confirm_img.png'), game_area)

full_slots_img = Target(cv2.imread('templates/spacecrypto/full_slots_img.png'), Area(470, 80, 70, 75))
btn_close_img = Target(cv2.imread('templates/spacecrypto/btn_close_img.png'), game_area)
btn_ok_img = Target(cv2.imread('templates/spacecrypto/btn_ok_img.png'), game_area)

boss_lose_img = Target(cv2.imread('templates/spacecrypto/boss_lose_img.png'), game_area)
boss_victory_img = Target(cv2.imread('templates/spacecrypto/boss_victory_img.png'), game_area)

class SpaceCryptoError(Exception):
    """Raised when SpaceCrypto shows an error"""
    pass

p = Printer("SpaceCrypto")

async def run_bot(next_action: Prodict):

    p.title('Starting SpaceCrypto')
    win = next_action.window
    scroll_limit = next_action.config.parameters.spaceship_scroll_limit

    try:
        area = Area(win.left, win.top, win.width, win.height)
        win.resizeTo(game_area.width, game_area.height)
        win.moveTo(game_area.left, game_area.top)
        win.activate()

        await handle_error_async()
        await get_game_ready()

        await handle_error_async()
        await prepare_spaceship_to_fight()

        await handle_error_async()
        await start_fight(scroll_limit)

        wait_for_spaceship_replacement_sec = next_action.config.intervals.wait_for_spaceship_replacement_sec

        min_wait = next_action.config.parameters.extra_random_wait_time_min_sec
        max_wait = next_action.config.parameters.extra_random_wait_time_max_sec
        extra_random_seconds = random.randint(min_wait, max_wait)
        next_action.schedules.wait_for_spaceship_replacement = get_now() + wait_for_spaceship_replacement_sec + extra_random_seconds   
    except:
        traceback.print_stack()
        raise
    
    finally:
        win.moveTo(area.left, area.top)
        win.resizeTo(area.width, area.height)   

    return next_action


def get_now():
    return datetime.timestamp(datetime.now())


async def get_game_ready():

    p.info('Checking if you are logged')
    if not tob.anyone(tob.verify_target_exists, [btn_fight_boss_img, btn_spaceship_inventory_img]):
        p.info('It looks like you are not logged')

        p.info('Possibly waiting unity loading screen')
        tob.wait_target_appear_disappear(target=loading_unity_img, expected_result=False)
       
        if not tob.verify_target_exists(btn_play_img, confidence=0.85):

            p.info('Possibly waiting for connect wallet button')
            tob.wait_target_appear_disappear(target=btn_connect_wallet_img, expected_result=True, confidence=0.85)

            p.info('Connecting to wallet')
            await tob.click_target_center_async(btn_connect_wallet_img, confidence=0.85)
            await handle_error_async()

            p.info('Signing to metamask')
            await metamask.signin()
            await handle_error_async()

        p.info('Waiting play button')
        tob.wait_target_appear_disappear(target=btn_play_img, expected_result=True, confidence=0.85)

        p.info('Entering the game')
        await tob.click_target_center_async(btn_play_img)


async def prepare_spaceship_to_fight(): 

    await check_confirm_buttons_async()

    if tob.safe_retry(tob.verify_target_exists, [btn_fight_boss_img], expected_result=True) == False:

        await check_confirm_buttons_async()

        p.info('Surrendering and starting from beginning again')
        await surrender_fight()

        await check_confirm_buttons_async()

        p.info('Traveling to spaceship inventory')
        while(tob.verify_target_exists(btn_spaceship_inventory_img)):
            await tob.click_target_center_async(btn_spaceship_inventory_img, sleep_after_click_sec=2)
        
        await wait_processing_async()

        p.info('Waiting for inventory')
        tob.wait_target_appear_disappear(btn_fight_boss_img, expected_result=True)


async def start_fight(scroll_limit: int):

    scroll_count = 0
    await asyncio.sleep(3)
    
    p.info('Selecting until full slots, this can take a long time')
    while not tob.verify_target_exists(full_slots_img, confidence=0.99):
        click_result = await tob.safe_click_target_center_async(btn_spaceship_fight_img, 
                                                x_offset=-20,  y_offset=-3, 
                                                max_x_precision_offset=10, max_y_precision_offset=6,
                                                sleep_after_click_sec=1, confidence=0.966) 

        if click_result == False:
            if scroll_count <= scroll_limit:
                scroll_count += 1
                await tob.hold_move_async(270, 300, 290, 125, 
                                        max_x_precision_offset=20, max_y_precision_offset=3,
                                        min_move_duration=0.5, max_move_duration=0.8)
            else:
                break
        
        if(tob.verify_target_exists(btn_close_img)):
            raise SpaceCryptoError("SpaceCrypto showed an error. Restarting...")

    await handle_error_async()

    p.info('Entering the space fight')
    await tob.click_target_center_async(btn_fight_boss_img) 
    await check_confirm_buttons_async()
   

async def surrender_fight():
    
    await tob.safe_retry_async(tob.click_target_center_async, [btn_surrender_img], max_attempts=3)
    await handle_error_async()

    tob.wait_target_appear_disappear(btn_surrender_confirm_img, expected_result=True)
    await tob.click_target_center_async(btn_surrender_confirm_img)
    await handle_error_async()

    await wait_processing_async()


async def wait_processing_async():
    p.info('Waiting processing...')
    tob.wait_target_appear_disappear(processing_img, expected_result=True)


async def check_confirm_buttons_async():
    p.info('Checking possible loss/victory confirm button')
    while tob.anyone(tob.verify_target_exists, [boss_lose_img, boss_victory_img]):
        await tob.safe_retry(tob.safe_click_target_center_async, [btn_victory_confirm_img], max_attempts=3)
        await tob.safe_retry(tob.safe_click_target_center_async, [btn_loss_confirm_img], max_attempts=3)
        await asyncio.sleep(2)
    

async def handle_error_async():

    p.info('Checking possible errors')
    if tob.safe_retry(tob.verify_target_exists, [btn_close_img], max_attempts=3, expected_result=True):
        await tob.click_target_center_async(btn_close_img, sleep_after_click_sec=2)
        raise SpaceCryptoError("SpaceCrypto showed an error. Restarting...")

    if tob.safe_retry(tob.verify_target_exists, [btn_ok_img], max_attempts=3, expected_result=True):
        await tob.click_target_center_async(btn_ok_img, sleep_after_click_sec=2)
        raise SpaceCryptoError("SpaceCrypto showed an error. Restarting...")