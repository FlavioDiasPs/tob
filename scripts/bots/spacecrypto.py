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
low_ammo_img = Target(cv2.imread('templates/spacecrypto/low_ammo_img.png'), game_area)
btn_close_img = Target(cv2.imread('templates/spacecrypto/btn_close_img.png'), game_area)
btn_ok_img = Target(cv2.imread('templates/spacecrypto/btn_ok_img.png'), game_area)
btn_wait_unresponsive_img = Target(cv2.imread('templates/spacecrypto/btn_wait_unresponsive_img.png'), game_area)

btn_repair = Target(cv2.imread('templates/spacecrypto/btn_repair.png'), game_area)
btn_yes = Target(cv2.imread('templates/spacecrypto/btn_yes.png'), game_area)
btn_page_down = Target(cv2.imread('templates/spacecrypto/btn_end.png'), game_area)
btn_page_up = Target(cv2.imread('templates/spacecrypto/btn_start.png'), game_area)

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

        wait_for_surrender_diff = 0
        if 'wait_for_surrender' in next_action.schedules:
            wait_for_surrender_diff = get_now() - next_action.schedules.wait_for_surrender

        if not tob.anyone(tob.verify_target_exists, [btn_fight_boss_img, btn_spaceship_inventory_img]):
            wait_for_surrender_diff = 0

        if wait_for_surrender_diff >= 0:

            await handle_error_async()
            await get_game_ready()

            await handle_error_async()
            await prepare_spaceship_to_fight()

            await handle_error_async()
            await start_fight(scroll_limit)

            wait_for_surrender_sec = next_action.config.intervals.wait_for_surrender_sec
            next_action.schedules.wait_for_surrender = get_now() + wait_for_surrender_sec

        else:
            await handle_error_async()
            await check_confirm_buttons_async()

        time_to_speed_victory_sec = next_action.config.intervals.time_to_speed_victory_sec
        next_action.schedules.time_to_speed_victory = get_now() + time_to_speed_victory_sec

    except:
        traceback.print_exc()
        await tob.refresh_page()
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

        retry_count = 0
        p.info('Traveling to spaceship inventory')
        while(tob.verify_target_exists(btn_spaceship_inventory_img)):
            await check_confirm_buttons_async()
            await tob.click_target_center_async(btn_spaceship_inventory_img, sleep_after_click_sec=2)

            retry_count += 1
            if retry_count > 4:
                await tob.refresh_page()
                raise SpaceCryptoError('The game probably got stuck. Restarting...')
        
        await wait_processing_async()

        p.info('Waiting for inventory')
        tob.wait_target_appear_disappear(btn_fight_boss_img, expected_result=True)


async def start_fight(scroll_limit: int):

    await asyncio.sleep(3)

    p.info('Removing low ammo spaceships, this can take a long time')
    await remove_low_ammo_spaceships_async()

    p.info('Repairing useless ships')
    await repair_useless_ships()

    p.info('Selecting until full slots, this can take a long time')
    await choose_spaceships_async(scroll_limit)
    await handle_error_async()

    p.info('Entering the space fight')
    retry_count = 0
    while(tob.verify_target_exists(btn_fight_boss_img)):
        await check_confirm_buttons_async()
        await tob.safe_click_target_center_async(btn_fight_boss_img, sleep_after_click_sec=1) 

        retry_count += 1
        if retry_count > 4:
            await tob.refresh_page()
            raise SpaceCryptoError('The game probably got stuck. Restarting...')

    await check_confirm_buttons_async()


async def remove_low_ammo_spaceships_async():

    while(tob.verify_target_exists(low_ammo_img, confidence=0.95)):
        await tob.safe_click_target_center_async(low_ammo_img, confidence=0.95,
                                                x_offset=22, y_offset=-5,
                                                max_y_precision_offset=3, max_x_precision_offset=3,
                                                sleep_after_click_sec=0)


async def repair_useless_ships():

    await tob.safe_click_target_center_async(btn_page_down, confidence=0.95, sleep_after_click_sec=1,
                                            max_x_precision_offset=1, max_y_precision_offset=1)

    await scroll_down_for_repair()

    while(tob.verify_target_exists(btn_repair)):
        await tob.safe_click_target_center_async(btn_repair, sleep_after_click_sec=1)
        await tob.safe_click_target_center_async(btn_yes, sleep_after_click_sec=1)
        await handle_error_async()

        if tob.verify_target_exists(btn_repair) == False:
            await scroll_down_for_repair(1)

    await tob.safe_click_target_center_async(btn_page_up, confidence=0.95, sleep_after_click_sec=1,
                                            max_x_precision_offset=1, max_y_precision_offset=1)
    await scroll_up_for_repair()


async def scroll_down_for_repair(scroll_limit = 6):
    scroll_count = 0
    while scroll_count < scroll_limit:
        if scroll_count <= scroll_limit:
            scroll_count += 1
            await tob.hold_move_release_async(270, 300, 290, 25, 
                                    max_x_precision_offset=20, max_y_precision_offset=3)


async def scroll_up_for_repair():
    scroll_count = 0
    scroll_limit = 6
    while scroll_count < scroll_limit:
        if scroll_count <= scroll_limit:
            scroll_count += 1
            await tob.hold_move_release_async(290, 125, 270, 500, 
                                    max_x_precision_offset=20, max_y_precision_offset=3)
                                                sleep_after_click_sec=0.1)
        tob.click()
        await asyncio.sleep(0.08)
        tob.click()
        await asyncio.sleep(0.08)
        tob.click()
        await asyncio.sleep(0.08)
        tob.click()
        await asyncio.sleep(0.08)


async def choose_spaceships_async(scroll_limit: int):
    scroll_count = 0

    while not tob.verify_target_exists(full_slots_img, confidence=0.99):
        click_result = await tob.safe_click_target_center_async(btn_spaceship_fight_img, 
                                                x_offset=-20,  y_offset=-3, 
                                                max_x_precision_offset=10, max_y_precision_offset=10,
                                                sleep_after_click_sec=0, confidence=0.92) 

        tob.click()
        await asyncio.sleep(0.08)
        tob.click()
        await asyncio.sleep(0.08)
        tob.click()
        await asyncio.sleep(0.08)
        tob.click()
        await asyncio.sleep(0.08)
        
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
    tob.wait_target_appear_disappear(processing_img, expected_result=False)


async def check_confirm_buttons_async():
    retry_count = 0
    p.info('Checking possible loss/victory confirm button')
    while tob.anyone(tob.verify_target_exists, [boss_lose_img, boss_victory_img]):
        await tob.safe_retry(tob.safe_click_target_center_async, [btn_victory_confirm_img], max_attempts=1)
        await tob.safe_retry(tob.safe_click_target_center_async, [btn_loss_confirm_img], max_attempts=1)
        await tob.safe_retry(tob.safe_click_target_center_async, [btn_surrender_confirm_img], max_attempts=1)
        await handle_error_async()

        retry_count += 1
        if retry_count > 4:
            await tob.refresh_page()
            raise SpaceCryptoError('The game probably got stuck. Restarting...')
    

async def handle_error_async():

    p.info('Checking possible errors')
    if tob.safe_retry(tob.verify_target_exists, [btn_wait_unresponsive_img], max_attempts=3, expected_result=True):
        await tob.click_target_center_async(btn_wait_unresponsive_img, sleep_after_click_sec=2)
        await asyncio.sleep(3)
        await tob.refresh_page()
        raise SpaceCryptoError("SpaceCrypto showed an error. Unresponsive. Restarting...")

    if tob.safe_retry(tob.verify_target_exists, [btn_close_img], max_attempts=3, expected_result=True):
        await tob.click_target_center_async(btn_close_img, sleep_after_click_sec=2)
        raise SpaceCryptoError("SpaceCrypto showed an error. Close button Restarting...")

    if tob.safe_retry(tob.verify_target_exists, [btn_ok_img], max_attempts=3, expected_result=True):
        await tob.click_target_center_async(btn_ok_img, sleep_after_click_sec=2)
        raise SpaceCryptoError("SpaceCrypto showed an error. Ok Button Restarting...")
