import asyncio
import random
import cv2

from datetime import datetime
from prodict import Prodict 

import helpers.tober as tob
import helpers.metamask as metamask
from helpers.tober import Area, Target
from helpers.printfier import Printer


game_area = Area(-8, -8, 685 , 520)
p = Printer("LunaRush")
   
battle_not_ended_yet_sec = 0
wait_for_battle_sec = 1
wait_for_energy_sec = 2 

loading = Target(cv2.imread('templates/lunarush/loading.png'), game_area)
helios_brand = Target(cv2.imread('templates/lunarush/helios_brand.png'), game_area)
btn_login_with_metamask = Target(cv2.imread('templates/lunarush/btn_login_with_metamask.png'), game_area)

btn_boss_hunt_start_game = Target(cv2.imread('templates/lunarush/btn_boss_hunt_start_game.png'), Area(60, 145, 145, 215))
btn_tap_to_open = Target(cv2.imread('templates/lunarush/btn_tap_to_open.png'), game_area)
btn_available_boss = Target(cv2.imread('templates/lunarush/btn_available_boss.png'), game_area)

in_battle_versus = Target(cv2.imread('templates/lunarush/in_battle_versus.png'), Area(315, 90, 40, 30))
btn_boss_hunt = Target(cv2.imread('templates/lunarush/btn_boss_hunt.png'), Area(490, 390, 150, 50))
 
selected_hero_no_energy = Target(cv2.imread('templates/lunarush/selected_hero_no_energy.png'), Area(160, 230, 370, 30))
selected_hero_energy = Target(cv2.imread('templates/lunarush/selected_hero_energy.png'), Area(160, 230, 370, 30))

unselected_hero_energy = Target(cv2.imread('templates/lunarush/unselected_hero_energy.png'), Area(15, 150, 135, 280))
unselected_hero_energy_part2 = Target(cv2.imread('templates/lunarush/unselected_hero_energy.png'), Area(20, 250, 130, 180))

notice = Target(cv2.imread('templates/lunarush/notice.png'), game_area) 
defeat = Target(cv2.imread('templates/lunarush/defeat.png'), game_area  )
victory = Target(cv2.imread('templates/lunarush/victory.png'), game_area)
error = Target(cv2.imread('templates/lunarush/error.png'), game_area)
window_is_open = Target(cv2.imread('templates/lunarush/window_is_open.png'), game_area)
 
loading_1 = Target(cv2.imread('templates/lunarush/in_game_loading.png'), Area(600, 390, 40, 40)) 
loading_2 = Target(cv2.imread('templates/lunarush/in_game_loading_2.png'), Area(600, 390, 40, 40)) 


class LunaRushError(Exception):
    """Raised when LunaRush shows an error""" 
    pass

  
async def run_bot(next_action: Prodict):
    
    p.title('Starting LunaRush')
    win = next_action.window

    try:
        if win.isMinimized:
            win.restore()

        area = Area(win.left, win.top, win.width, win.height)
        win.resizeTo(game_area.width, game_area.height)
        win.moveTo(game_area.left, game_area.top)
        win.activate()

        await asyncio.sleep(2)
        next_schedule = await heroes_battle()
        next_action = await calculate_next_schedule(next_schedule, next_action)
   
    finally:
        win.moveTo(area.left, area.top)
        win.resizeTo(area.width, area.height)

    if 'wait_for_energy' in next_action.schedules:
        p.info("There are no fights left. Minimizing to save resources")
        win.minimize()
  
    return next_action


def get_now():
    return datetime.timestamp(datetime.now())

 
async def heroes_battle():

    if tob.safe_retry(
        tob.verify_target_exists, (in_battle_versus, 0.7), max_attempts=4, expected_result=True): 
        await tob.safe_click_target_center_async(in_battle_versus, confidence=0.7)
        p.info('Battle is not finished yet, waiting an extra time')
        return battle_not_ended_yet_sec

    if tob.verify_target_exists(window_is_open) == False:     
        raise Exception('The window was not open')

    await handle_login()
    await handle_preparation()

    p.info('Removing selected heroes without energy')
    await tob.click_all_targets_center_async(selected_hero_no_energy, x_offset=random.randint(50, 70))   
    await asyncio.sleep(3)

    return await prepare_and_fight()


async def calculate_next_schedule(battle_result, next_action: Prodict):
    next_action.schedules = Prodict({})
    conf = next_action.config

    if battle_result == wait_for_battle_sec: 
        next_action.schedules.wait_for_battle = get_now() + conf.intervals.wait_for_battle_sec

    elif battle_result == wait_for_energy_sec:  
        next_action.schedules.wait_for_energy = get_now() + conf.intervals.wait_for_energy_sec

    elif battle_result == battle_not_ended_yet_sec:
        next_action = await check_battle_not_ended_yet(next_action, conf)
        
    else:
        next_action.schedules.unknow_schedule = get_now() + 500

    return next_action

    
async def check_battle_not_ended_yet(next_action: Prodict, conf: Prodict):
    if 'ingame' not in next_action:
        next_action.ingame = Prodict({})

    if 'battle_not_ended_yet_count' not in next_action.ingame:
        next_action.ingame.battle_not_ended_yet_count = 0
                    
    next_action.ingame.battle_not_ended_yet_count += 1

    p.info(f'Battle not ended yet: {next_action.ingame.battle_not_ended_yet_count}/{conf.parameters.battle_not_ended_max_retries}')
    if next_action.ingame.battle_not_ended_yet_count > conf.parameters.battle_not_ended_max_retries:
        next_action.schedules.battle_stuck_refreshing_page = get_now() + 1
        await tob.refresh_page()
    else:
        next_action.schedules.battle_not_ended_yet = get_now() + conf.intervals.battle_not_ended_yet_sec

    return next_action


async def handle_login():

    if tob.verify_target_exists(error):
        await tob.refresh_page()
        await asyncio.sleep(4)

    if tob.anyone(tob.verify_target_exists, [loading, btn_login_with_metamask, helios_brand]):

        p.info('Waiting loading')
        tob.safe_retry(tob.verify_target_exists, [loading], max_attempts=40, expected_result=False)

        await asyncio.sleep(2)
        p.info('Waiting helios brand')
        tob.safe_retry(tob.verify_target_exists, [helios_brand], max_attempts=40, expected_result=False)

        await asyncio.sleep(2)
        p.info('Login in with metamask')
        await tob.click_target_center_async(btn_login_with_metamask, sleep_after_click_sec=2)

        p.info('Signin metamask')
        await metamask.signin()

        p.info('Entering the game')
        tob.retry(tob.verify_target_exists, [btn_boss_hunt_start_game], max_attempts=40, expected_result=True)


async def handle_preparation():

    if tob.verify_target_exists(btn_boss_hunt):
        return 

    elif tob.safe_retry(tob.verify_target_exists, [btn_tap_to_open], max_attempts=10, expected_result=True):  
        p.info('Taking rewards from battle')
         
        while tob.anyone(tob.verify_target_exists, [defeat, victory]):
            await tob.click_target_center_async(btn_tap_to_open, sleep_after_click_sec=2)
            await tob.click_location_async(x=random.randint(250, 350), y=random.randint(250, 350))

    elif tob.safe_retry(tob.verify_target_exists, [victory], max_attempts=10, expected_result=True): 
        p.info('Continuing to next battle afeter victory')
        await asyncio.sleep(2)
        await tob.click_location_async(x=random.randint(250, 350), y=random.randint(250, 350))

    elif tob.safe_retry(tob.verify_target_exists, [defeat], max_attempts=10, expected_result=True): 
        p.info('Continuing to next battle after defeat')
        await asyncio.sleep(2)
        await tob.click_location_async(x=random.randint(250, 350), y=random.randint(250, 350))
 
    elif tob.verify_target_exists(btn_boss_hunt_start_game): 
        p.info('Entering boss fight') 
        await tob.click_target_center_async(btn_boss_hunt_start_game, sleep_after_click_sec=0.5)
    
    
    p.info('Checking if will need to choose a new boss to fight')
    await asyncio.sleep(3)
    await tob.safe_click_target_center_async(btn_available_boss, sleep_after_click_sec=0.5) 
    await handle_error_async()
    

async def prepare_and_fight():
    p.info('Checking amount of selected heroes able to fight')   

    amount_heroes_selected = tob.verify_target_ocorrency_amount(selected_hero_energy) 
    if amount_heroes_selected >= 3:
        await run_battle()
        return wait_for_battle_sec

    amount_heroes_selected = await add_heroes_to_fight(unselected_hero_energy, amount_heroes_selected)
    if amount_heroes_selected >= 3:
        await run_battle()     
        return wait_for_battle_sec

    await tob.hold_move_async(150, 200, 154, 296)
    amount_heroes_selected = await add_heroes_to_fight(unselected_hero_energy, amount_heroes_selected)
        
    if amount_heroes_selected >= 3:
        await run_battle() 
        return wait_for_battle_sec 

    await tob.hold_move_async(150, 296, 154, 370)
    amount_heroes_selected = await add_heroes_to_fight(unselected_hero_energy_part2, amount_heroes_selected)    
    
    await tob.hold_move_async(150, 370, 154, 200)

    if amount_heroes_selected <= 0: 
        return wait_for_energy_sec
    else: 
        await run_battle()
        return wait_for_battle_sec


async def add_heroes_to_fight(target, amount_heroes_selected = 0):
    
    tob.move(random.uniform(30, 120), random.uniform(150,  190))

    p.info('Selecting more heroes to participate in battle')
    heroes_locations = await tob.find_targets_centers_async(target, confidence=0.85)

    for hero_location in heroes_locations:        
  
        await tob.click_location_async(x=hero_location[0], y=hero_location[1], 
                                        y_offset=random.randint(-70, -50), sleep_after_click_sec=1)
        await wait_loading()

        amount_heroes_selected += 1  
        if amount_heroes_selected == 3:
            return amount_heroes_selected

    return amount_heroes_selected


async def run_battle():
    p.info("Battling")      

    await wait_loading()
    await tob.click_target_center_async(btn_boss_hunt, sleep_after_click_sec=2)

    await wait_in_battle()
    await tob.click_target_center_async(in_battle_versus, confidence=0.7, sleep_after_click_sec=2)
 

async def wait_in_battle():
    retry_count = 0
    retry_limit = 10

    while retry_count < retry_limit and tob.verify_target_exists(in_battle_versus, confidence=0.8) == False:

        if tob.verify_target_exists(notice):
            tob.click()
            return False

        await handle_error_async()
        await wait_loading()
        tob.click()

        retry_count += 1

    if retry_count > retry_limit:
        return False

    return True


async def handle_error_async():

    if tob.verify_target_exists(error):
        await tob.click_location_async(random.uniform(100, 300), random.uniform(100, 300))
        raise Exception("Luna Rush showed an error")


async def wait_loading():

    while(tob.anyone_multi_param(tob.verify_target_exists, [(loading_1, 0.6), (loading_2, 0.6)])):
        p.r_info("Waiting load")
        await asyncio.sleep(0.1)