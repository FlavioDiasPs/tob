import asyncio
import cv2
import traceback

from datetime import datetime
from prodict import Prodict 

import helpers.tober as tob
import helpers.metamask as metamask

from helpers.printfier import Printer
from helpers.tober import Target

btn_battlefield_img = Target(cv2.imread('templates/cryptopiece/btn_battlefield.png'))
btn_battlefield_merc_down_img = Target(cv2.imread('templates/cryptopiece/btn_battlefield_merc_down.png'))
btn_battle_img = Target(cv2.imread('templates/cryptopiece/btn_battle.png'))
btn_battlefield_battle_claim_img = Target(cv2.imread('templates/cryptopiece/btn_battlefield_battle_claim.png'))
btn_battlefield_battle_close_img = Target(cv2.imread('templates/cryptopiece/btn_battlefield_battle_close.png'))
btn_battlefield_criminal_img = Target(cv2.imread('templates/cryptopiece/criminal_70.png'))
battlefield_stamina_img = Target(cv2.imread('templates/cryptopiece/battlefield_stamina.png'))
battlefield_wait_battle_img = Target(cv2.imread('templates/cryptopiece/battlefield_wait_battle.png'))
not_enough_stamina_img = Target(cv2.imread('templates/cryptopiece/not_enough_stamina.png'))
not_enough_stamina_2_img = Target(cv2.imread('templates/cryptopiece/not_enough_stamina_2.png'))
no_remaining_matches_img = Target(cv2.imread('templates/cryptopiece/no_remaining_matches.png'))

class CryptoPieceError(Exception):
    """Raised when CryptoPiece shows an error"""
    pass

p = Printer("CryptoPiece")

async def run_bot(next_action: Prodict):

    p.title('Starting CryptoPiece')

    await get_game_ready()
    await merc_battle()

    wait_for_stamina = next_action.config.intervals.wait_for_stamina_sec
    next_action.schedules.wait_for_stamina = get_now() + wait_for_stamina           

    return next_action


def get_now():
    return datetime.timestamp(datetime.now())


async def get_game_ready():
    await tob.refresh_page()
    await asyncio.sleep(3)


async def merc_battle():   

    p.info('Finding current mercs')
    mercs_centers = await tob.find_targets_centers_async(btn_battlefield_merc_down_img, confidence=0.7)
    
    p.info('Selecting merc')
    for (merc_pos_x, merc_pos_y) in mercs_centers:
        await tob.click_location_async(x=merc_pos_x, y=merc_pos_y, y_offset=-50, sleep_after_click_sec=2)
        
        p.info('Starting Merc Battle')
        while(tob.safe_retry(verify_able_to_batte, max_attempts=3, expected_result=True)):
            
            (crim_x, crim_y) = (await tob.find_targets_centers_async(btn_battlefield_criminal_img))[0]
            await tob.click_location_async(crim_x, crim_y, x_offset=-100)

            await tob.click_target_center_async(btn_battle_img)
            await metamask.signin()     
            
            await wait_battle_results()
            await tob.click_location_async(x=100, y=200)

        p.info('Battle has ended successfully')


def verify_able_to_batte():

    has_stamina = tob.verify_target_exists(battlefield_stamina_img, confidence=0.98)
    has_matches = not tob.verify_target_exists(no_remaining_matches_img, confidence=0.98)

    if(has_stamina and has_matches): 
        return True
    else:
        return False 


async def wait_battle_results():
            
    tob.retry(tob.verify_target_exists, [battlefield_wait_battle_img], expected_result=False, max_attempts=100)
        
    battle_ends_targets = [
                            btn_battlefield_battle_claim_img, 
                            btn_battlefield_battle_close_img,
                            not_enough_stamina_img, 
                            not_enough_stamina_2_img  
                        ]

    tob.retry(tob.anyone, [tob.verify_target_exists, battle_ends_targets], expected_result=True, max_attempts=100)

    