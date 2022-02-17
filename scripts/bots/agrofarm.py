import asyncio
import cv2
import traceback

from datetime import datetime
from prodict import Prodict

import helpers.tober as tob
import helpers.metamask as metamask
from helpers.printfier import Printer
from helpers.tober import Target, Area

game_area = Area(-8, -8, 812 , 500)

btn_connect = Target(cv2.imread('templates/agrofarm/btn_connect.png'), game_area)
btn_disconnect = Target(cv2.imread('templates/agrofarm/btn_disconnect.png'), game_area)
btn_choose_wallet = Target(cv2.imread('templates/agrofarm/btn_choose_wallet.png'), game_area)
btn_my_farm = Target(cv2.imread('templates/agrofarm/btn_my_farm.png'), game_area)
btn_collect = Target(cv2.imread('templates/agrofarm/btn_collect.png'), game_area)
btn_ok = Target(cv2.imread('templates/agrofarm/btn_ok.png'), game_area)
btn_my_seeds = Target(cv2.imread('templates/agrofarm/btn_my_seeds.png'), game_area)
btn_crop = Target(cv2.imread('templates/agrofarm/btn_crop.png'), game_area)
btn_plant_now = Target(cv2.imread('templates/agrofarm/btn_plant_now.png'), game_area)
wait_0_minutes = Target(cv2.imread('templates/agrofarm/wait_0_minutes.png'), game_area)
wait_1_minutes = Target(cv2.imread('templates/agrofarm/wait_1_minutes.png'), game_area)
wait_2_minutes = Target(cv2.imread('templates/agrofarm/wait_2_minutes.png'), game_area)
wait_3_minutes = Target(cv2.imread('templates/agrofarm/wait_3_minutes.png'), game_area)
wait_4_minutes = Target(cv2.imread('templates/agrofarm/wait_4_minutes.png'), game_area)
no_crops_left = Target(cv2.imread('templates/agrofarm/no_crops_left.png'), game_area)
loading_amount_crops_left = Target(cv2.imread('templates/agrofarm/loading_amount_crops_left.png'), game_area)

class AgroFarmError(Exception):
    """Raised when AgroFarm shows an error"""
    pass

p = Printer("AgroFarm")

async def run_bot(next_action: Prodict):

    p.title('Starting AgroFarm')
    win = next_action.window

    try:
        # area = Area(win.left, win.top, win.width, win.height)
        win.restore()
        win.resizeTo(game_area.width, game_area.height)
        win.moveTo(game_area.left, game_area.top)
        win.activate()

        await get_game_ready()
        crop_plant_next_schedule = await crop_and_plant()

        if crop_plant_next_schedule == None:
            crop_plant_next_schedule = next_action.config.intervals.wait_time_when_no_crop_left_sec

        next_action.schedules.crop_plant_schedule = get_now() + crop_plant_next_schedule   

    finally:
        # win.moveTo(area.left, area.top)
        # win.resizeTo(area.width, area.height)
        win.minimize()

    return next_action


def get_now():
    return datetime.timestamp(datetime.now())


async def is_connected():
    ''' Check if you are connected to your wallet or have been disconnected from any errors '''

    p.info('Checking if you are connected')
    if tob.verify_target_exists(btn_connect):
        p.info('It looks like you are not connected')
        return False
    else:
        p.info('You might be connected')
        return True


async def get_game_ready():
    if await is_connected() == False:
        return await connect_wallet()


async def connect_wallet():
    ''' Sign in, connect, or reconnect the game with metamask '''
    print(' ** Connection wallet')

    await tob.click_target_center_async(btn_connect)
    await tob.click_target_center_async(btn_choose_wallet)

    await metamask.next()
    await metamask.connect()

    if await check_game_connected() == False:
        raise Exception("Couldn't connect to metamask")


async def check_game_connected():

    p.info('Loading...')
    custom_error = "Couldn't connect to the game"
    return tob.retry(tob.verify_target_exists, [btn_disconnect], 
                    expected_result=True, 
                    custom_error=custom_error)


async def crop_and_plant():

    p.info('Checking plants to crop')
    await tob.click_target_center_async(btn_my_farm, sleep_after_click_sec=1)

    see_btn_collect = tob.safe_retry(tob.verify_target_exists, [btn_collect], max_attempts=2, expected_result=True)
    see_btn_seed = tob.safe_retry(tob.verify_target_exists, [btn_my_seeds], max_attempts=2, expected_result=True)
    if see_btn_collect == False and see_btn_seed == False:
        return await find_minutes_to_wait() * 60

    while(tob.verify_target_exists(btn_collect)):
        await tob.click_target_center_async(btn_collect)
        await tob.safe_click_target_center_async(btn_ok, sleep_after_click_sec=0.5)
    
    p.info('Checking seeds to plant')
    await tob.click_target_center_async(btn_my_seeds, sleep_after_click_sec=5)
    
    tob.safe_retry(tob.verify_target_exists, [loading_amount_crops_left], expected_result=False)

    if tob.verify_target_exists(no_crops_left):
        p.info('There are no crops left')
        return None

    crop_made = 0
    crop_amount = 1
    while crop_made < crop_amount:
        await tob.click_target_center_async(btn_plant_now)
        await asyncio.sleep(1)

        crop_amount = tob.verify_target_ocorrency_amount(btn_crop)
        await tob.click_target_center_async(btn_crop)
        await tob.click_target_center_async(btn_ok)
        crop_made += 1

    return await find_minutes_to_wait() * 60


async def find_minutes_to_wait():

    wait_time_min = 0
    p.info('Checking minutes left to next crop')
    await tob.click_target_center_async(btn_my_farm)

    if (tob.verify_target_exists(wait_4_minutes)):
        wait_time_min = 5
    elif (tob.verify_target_exists(wait_3_minutes)):
        wait_time_min = 4
    elif (tob.verify_target_exists(wait_2_minutes)):
        wait_time_min = 3
    elif (tob.verify_target_exists(wait_1_minutes)):
        wait_time_min = 2
    elif (tob.verify_target_exists(wait_0_minutes)):
        wait_time_min = 1
    else:
        print(' **** Couldnt find any wait time. Retrying')
        wait_time_min = -1

    p.info(f'We will wait for {wait_time_min} minutes')
    return wait_time_min