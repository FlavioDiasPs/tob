import asyncio
import math
import random
import cv2
import traceback

from datetime import datetime
from prodict import Prodict 

import helpers.tober as tob
from helpers.tober import Area, Target
from helpers.printfier import Printer

btn_boss_fight = Target(cv2.imread('templates/lunarush/1_btn_boss_fight.png'), Area(230, 180, 290, 360))
btn_tap_to_open = Target(cv2.imread('templates/lunarush/1_btn_tap_to_open.png'), Area(580, 550,  210, 70))
btn_available_boss = Target(cv2.imread('templates/lunarush/2_btn_available_boss.png'))

in_battle_versus = Target(cv2.imread('templates/lunarush/2_in_battle_versus.png'), Area(650, 120, 70, 50))
btn_boss_hunt = Target(cv2.imread('templates/lunarush/3_btn_boss_hunt.png'), Area(920, 560, 210, 80))

selected_hero_no_energy = Target(cv2.imread('templates/lunarush/6_selected_hero_no_energy.png'), Area(425, 315, 565, 50))
selected_hero_energy = Target(cv2.imread('templates/lunarush/selected_hero_energy.png'), Area(425, 315, 565, 50))

unselected_hero_energy = Target(cv2.imread('templates/lunarush/6_unselected_hero_energy.png'), Area(180, 200, 240, 410))
unselected_hero_energy_part2 = Target(cv2.imread('templates/lunarush/6_unselected_hero_energy.png'), Area(180, 350, 240, 280))

notice = Target(cv2.imread('templates/lunarush/notice.png'))
defeat = Target(cv2.imread('templates/lunarush/defeat.png'))
victory = Target(cv2.imread('templates/lunarush/victory.png'))
error = Target(cv2.imread('templates/lunarush/error.png'))

loading_1 = Target(cv2.imread('templates/lunarush/in_game_loading.png'), Area(1100, 565, 60, 65))
loading_2 = Target(cv2.imread('templates/lunarush/in_game_loading_2.png'), Area(1100, 565, 60, 65))


class LunaRushError(Exception):
    """Raised when LunaRush shows an error""" 
    pass


game_area = Area()
p = Printer("LunaRush")

battle_not_ended_yet_min = 0
wait_for_battle_min = 1
wait_for_energy_min = 2 

  
async def run_bot(next_action: Prodict):
    
    p.title('Starting LunaRush')

    result = await heroes_battle()
    next_action.schedules = Prodict({})

    if result == wait_for_battle_min: 
        next_action.schedules.wait_for_battle = get_now() + next_action.config.wait_for_battle_min * 60
    elif result == wait_for_energy_min:
                     
        dt = datetime.fromtimestamp(get_now())
        if dt.hour >= 0 and dt.hour <= 6:
            next_action.schedules.wait_for_energy = get_now() + 180 * 60 
        else:
            next_action.schedules.wait_for_energy = get_now() + next_action.config.wait_for_energy_min * 60

    elif result == battle_not_ended_yet_min:
        next_action.schedules.battle_not_ended_yet = get_now() + next_action.config.battle_not_ended_yet_min * 60
    else:
        next_action.schedules.unknow_schedule = get_now() + 500       
   
    return next_action


def get_now():
    return datetime.timestamp(datetime.now())


async def heroes_battle():

    if tob.verify_target_exists(in_battle_versus, confidence=0.7):
        p.info('Battle is not finished yet, waiting an extra time')
        return battle_not_ended_yet_min

    await handle_start()
    await handle_preparation()

    battle_result = False
    while(battle_result == False):

        p.info('Removing selected heroes without energy')
        await tob.click_all_targets_center_async(selected_hero_no_energy, x_offset=random.randint(65, 85))   
        await asyncio.sleep(3)

        p.info('Checking amount of selected heroes able to fight')   
        amount_heroes_selected = tob.verify_target_ocorrency_amount(selected_hero_energy) 
        if amount_heroes_selected >= 3:
            battle_result = await run_battle()
            continue 
    
        amount_heroes_selected += await add_heroes_to_fight(unselected_hero_energy, amount_heroes_selected)
        if amount_heroes_selected >= 3:
            battle_result = await run_battle()  
            continue   

        await tob.scroll(updown=-380, repeats=3)
        amount_heroes_selected += await add_heroes_to_fight(unselected_hero_energy, amount_heroes_selected)
         
        if amount_heroes_selected >= 3:
            battle_result = await run_battle()  
            continue

        await tob.scroll(updown=-380, repeats=3)  
        amount_heroes_selected += await add_heroes_to_fight(unselected_hero_energy_part2, amount_heroes_selected)    
      
        await tob.scroll(updown=500, repeats=5)

        if amount_heroes_selected <= 0:          
            return wait_for_energy_min   
        else: 
            battle_result = await run_battle()

    return battle_result
            
    
async def handle_start():

    if tob.verify_target_exists(btn_boss_hunt):
        return 

    elif tob.verify_target_exists(btn_boss_fight): 
        p.info('Entering boss fight') 
        await tob.click_target_center_async(btn_boss_fight, sleep_after_click_sec=0.5)
    
    elif tob.verify_target_exists(btn_tap_to_open):  
        p.info('Taking rewards from battle')
        
        while tob.anyone(tob.verify_target_exists, [defeat, victory]):
            await tob.click_target_center_async(btn_tap_to_open, sleep_after_click_sec=2)
            await tob.click_location_async(x=random.randint(250, 350), y=random.randint(250, 350))

    elif tob.anyone(tob.verify_target_exists, [defeat, victory]): 
        p.info('Continuing to next battle')
        await tob.click_location_async(x=random.randint(250, 350), y=random.randint(250, 350))


async def handle_preparation():

    p.info('Choosing available boss to fight')
    await asyncio.sleep(3)
    await tob.safe_click_target_center_async(btn_available_boss, sleep_after_click_sec=0.5) 
    await handle_error_async()
    
  
async def add_heroes_to_fight(target, amount_heroes_selected = 0):
    
    tob.move(random.uniform(250, 400), random.uniform(250,  400))

    p.info('Selecting more heroes to participate in battle')
    heroes_locations = await tob.find_targets_centers_async(target, confidence=0.90)

    for hero_location in heroes_locations:        

        await tob.click_location_async(x = hero_location[0], y = hero_location[1], y_offset=random.randint(-70, -50))
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

    return wait_for_battle_min
 

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