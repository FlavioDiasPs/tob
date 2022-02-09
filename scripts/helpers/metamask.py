import helpers.tober as tob
import asyncio
import cv2

from helpers.tober import Target

btn_metamask_connect = Target(cv2.imread('templates/metamask/btn_metamask_connect.png'))
btn_metamask_next = Target(cv2.imread('templates/metamask/btn_metamask_next.png'))
btn_metamask_sign = Target(cv2.imread('templates/metamask/btn_metamask_sign.png'))


async def metamask_click(btn):
    
    tob.activate_window_by_name("MetaMask Notification")    
    tob.retry(tob.verify_target_exists, [btn], max_attempts=100, attempt_delay=0.2, expected_result=True)
    
    while(tob.verify_target_exists(btn)):
        await tob.click_target_center_async(target=btn, max_attempts=100, attempt_delay=0.2)
        await asyncio.sleep(2)


async def signin():
    await metamask_click(btn_metamask_sign)
    await asyncio.sleep(1)
    

async def next():
    await metamask_click(btn_metamask_next)  
    await asyncio.sleep(1)  


async def connect():
    await metamask_click(btn_metamask_connect)
    await asyncio.sleep(1)

