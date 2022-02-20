import traceback
import pyautogui
import asyncio
import yaml
import keyboard

import bots.bombcrypto as bombcrypto_bot
import bots.agrofarm as agrofarm_bot
import bots.cryptopiece as cryptopiece_bot
import bots.lunarush as lunarush_bot
import bots.spacecrypto as spacecrypto_bot
import helpers.tober as tob
import handlers.action as action

from prodict import Prodict
from colorama import init
from datetime import datetime
from typing import List

from helpers.printfier import Printer
from runner import Runner


# action = {
#     'schedules': {
#         'name': datetime,
#         'name': datetime,
#         'name': datetime
#     },
#     'window': any,
#     'function': any,
#     'config': Prodict({}),
#     'bot_name': str
# }

pressed_enter = False
p = Printer(bot_name='TOB')
init(autoreset=True, convert=True)

async def main():
    global pressed_enter

    await boot(3)
    p.title('Starting TOB - The Only Bot')
    runner = Runner()

    while True:
        p.info('Taking active window')
        
        runner.all_configs = preparation()

        if pressed_enter == True:
            runner.next_action.schedules = {}
            pressed_enter = False

        runner = await run(runner)
        finalization(runner.all_configs)
        
        next_actions = get_next_actions(runner.all_actions)
        runner.next_action = next_actions[0]

        write_next_actions_summary(next_actions)
        await wait_next_action_time(next_actions=next_actions)


def preparation():
    global current_active_window
    
    p.info('Preparing to run')

    pyautogui.FAILSAFE = False
    tob.close_windows_by_name('Metamask Notification')
    
    current_active_window = pyautogui.getActiveWindow()
    all_bots_configs = Prodict(yaml.safe_load(open('config.yaml', 'r')))
    
    if all_bots_configs.tob['press_space_before_and_after_bot']:
        pyautogui.press('space')

    return all_bots_configs


def finalization(all_bots_configs: Prodict):
    current_active_window.activate()

    if all_bots_configs.tob['press_space_before_and_after_bot']:
        pyautogui.press('space')


async def run(runner: Runner):

    if runner.next_action:
        await action.run_action(runner)

    else:
        bot_configs = [bot_name for bot_name in runner.all_configs if bot_name != 'tob']

        for bot_name in bot_configs:
            runner.next_action = fill_next_action(runner.all_configs, bot_name)
            await action.run_action(runner)

    return runner


def fill_next_action(all_configs: Prodict, bot_name: str):
    next_action = Prodict({})
    next_action.bot_name = bot_name
    next_action.schedules = Prodict({}) 
    next_action.config = Prodict(all_configs[bot_name])

    if bot_name == 'bombcrypto':
        next_action.function = bombcrypto_bot.run_bot
    elif bot_name == 'agrofarm':
        next_action.function = agrofarm_bot.run_bot
    elif bot_name == 'cryptopiece':
        next_action.function = cryptopiece_bot.run_bot
    elif bot_name == 'lunarush':
        next_action.function = lunarush_bot.run_bot
    elif bot_name == 'spacecrypto':
        next_action.function = spacecrypto_bot.run_bot
    else:
        raise Exception("{bot_name} is not supported")

    return next_action


def write_next_actions_summary(next_actions: List[Prodict]):

    p.title('Actions in the line')
    for i in range(0, len(next_actions)):
        action = next_actions[i]
        action_schedule_items = Prodict(next_actions[i]).schedules.items()
        action_schedule_obj = min(action_schedule_items, key=lambda x: x[1])
        action_shcedule_desc = action_schedule_obj[0]
        action_schedule_sec = action_schedule_obj[1]
        window_title = action.window.title

        time_to_wait_datetime = datetime.fromtimestamp(action_schedule_sec)
        time_to_wait_formated = time_to_wait_datetime.strftime('%Hh:%Mm:%Ss')

        p.info(f'Bot window: {window_title} -> {action_shcedule_desc} at {time_to_wait_formated}')


async def wait_next_action_time(next_actions: List[Prodict]):
    next_action = next_actions[0]
    next_action_schedule_items = Prodict(next_actions[0]).schedules.items()
    next_action_schedule_obj = min(next_action_schedule_items, key=lambda x: x[1])
    
    next_action_schedule_desc = next_action_schedule_obj[0]
    next_action_schedule_sec = next_action_schedule_obj[1]

    print('')
    time_to_wait_sec = next_action_schedule_sec
    while(time_to_wait_sec > 0):

        now = datetime.timestamp(datetime.now())
        time_to_wait_sec = next_action_schedule_sec - now

        if time_to_wait_sec <= 0:
            time_to_wait_sec = 0

        time_to_wait_datetime = datetime.utcfromtimestamp(time_to_wait_sec)
        time_to_wait_formated = time_to_wait_datetime.strftime('%Hh:%Mm:%Ss')

        message = f'[tob] Next action: {next_action.window.title} -> {next_action_schedule_desc} in {time_to_wait_formated}'
        print(f' ## {message} ##', end='\r')
        await asyncio.sleep(1)

        if keyboard.is_pressed('enter'):
            global pressed_enter
            pressed_enter = True
            break


def get_next_actions(all_actions):
    actions = []

    for key in all_actions:
        actions = actions + all_actions[key]

    next_actions = sorted(
                            actions,
                            key=lambda a: min(a['schedules'].items(), 
                            key=lambda x: x[1])[1],
                            reverse=False
                        )

    return next_actions


async def boot(duration):
    while duration >= 0:
        p.r_info(f'Starting in {duration} seconds(s)..')
        await asyncio.sleep(1)
        duration -= 1


while(True):
    try:    

        asyncio.run(main())

    except:
        traceback.print_exc()