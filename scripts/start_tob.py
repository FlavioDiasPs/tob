import traceback
import pyautogui
import pygetwindow
import asyncio
import os
import yaml

import bots.bombcrypto as bombcrypto_bot
import bots.agrofarm as agrofarm_bot
import bots.cryptopiece as cryptopiece_bot
import bots.lunarush as lunarush_bot
import helpers.tober as tob
from prodict import Prodict
from colorama import init
from datetime import datetime
from typing import List

from helpers.printfier import Printer


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

last_window_amount_by_bot = Prodict({})
all_actions = Prodict({})
p = Printer(bot_name='TOB')

init(autoreset=True, convert=True)

async def main():

    await boot(3)
    p.title('Starting TOB - The Only Bot')

    next_action = None

    while True:
        p.info('Taking active window')
        current_active_window = pyautogui.getActiveWindow()
        pyautogui.FAILSAFE = False
        pyautogui.press('space')

        await run(next_action)

        current_active_window.activate()
        pyautogui.press('space')

        next_actions = get_next_actions()
        next_action = next_actions[0]

        write_next_actions_sumary(next_actions)
        await wait_next_action_time(next_actions=next_actions)


async def run(next_action: Prodict):

    p.info('Loading configs')
    all_bots_configs = Prodict(yaml.safe_load(open('config.yaml', 'r')))

    if next_action:
        await run_bot_windows(next_action)

    else:
        for bot_name in all_bots_configs:
            next_action = fill_next_action(next_action, bot_name, all_bots_configs)
            await run_bot_windows(next_action)

  
async def run_bot_windows(next_action: Prodict):

    p.info('Taking bot windows')
    bot_windows = get_bot_windows(next_action.config.window_name)

    bot_name_not_in_the_previous_list = not (next_action.bot_name in last_window_amount_by_bot)

    if (bot_name_not_in_the_previous_list or last_window_amount_by_bot[next_action.bot_name] != len(bot_windows)):
        all_actions[next_action.bot_name] = await run_all_windows(bot_windows, next_action)

    else:
        result = await run_single_action(next_action=next_action)
        index = get_action_index_by_window(bot_name=next_action.bot_name, window=result.window)
        all_actions[next_action.bot_name][index] = result

    last_window_amount_by_bot[next_action.bot_name] = len(bot_windows)


def fill_next_action(next_action: Prodict, bot_name: str, all_bots_configs: Prodict):
    next_action = Prodict({})
    next_action.schedules = Prodict({}) 
    next_action.bot_name = bot_name
    next_action.config = Prodict(all_bots_configs[bot_name])

    if bot_name == 'bombcrypto':
        next_action.function = bombcrypto_bot.run_bot
    elif bot_name == 'agrofarm':
        next_action.function = agrofarm_bot.run_bot
    elif bot_name == 'cryptopiece':
        next_action.function = cryptopiece_bot.run_bot
    elif bot_name == 'lunarush':
        next_action.function = lunarush_bot.run_bot
    else:
        raise Exception("{bot_name} is not supported")

    return next_action


async def boot(duration):
    while duration >= 0:
        p.r_info(f'Starting in {duration} seconds(s)..')
        await asyncio.sleep(1)
        duration -= 1


def get_bot_windows(window_name: str):
    amount_windows = 0
    while(amount_windows <= 0):
        windows = pygetwindow.getWindowsWithTitle(window_name)
        amount_windows = len(windows)

        if amount_windows <= 0:
            print(f"Rename all the windows to: {window_name}")
            os.system("pause")

    return windows


async def run_single_action(next_action: Prodict):
    p.info('Running action')
    
    await tob.retry_async(initialize_bot_window, [next_action.window], 100, 0.2)    
    return await wrap_bot_function(next_action)


async def run_all_windows(bot_windows, next_action: Prodict):
    result_actions = []

    p.info('Running action') 
    for bot_window in bot_windows:
        await tob.retry_async(initialize_bot_window, [bot_window], 100, 0.2)

        result_action = Prodict(await wrap_bot_function(next_action))
       
        result_action.window = bot_window
        result_actions.append(result_action)

    return result_actions


async def wrap_bot_function(next_action: Prodict):
    retry_count = 0
    retry_limit = 1
    retry_schedule_name = f'retry_failed_{next_action.bot_name}'

    param_action = Prodict(next_action.copy())
    bot_function = next_action.function
    
    while(retry_count <= retry_limit):
        try:

            if retry_schedule_name in param_action.schedules:
                param_action.schedules = Prodict({})

            return await bot_function(param_action)

        except:
            traceback.print_exc()
            await asyncio.sleep(2)
            retry_count += 1

    now = datetime.timestamp(datetime.now())
    next_action.schedules = Prodict({})
    next_action.schedules[retry_schedule_name] = now + 30 * 60

    return next_action


async def initialize_bot_window(bot_window):
    bot_window.restore()
    bot_window.moveTo(-8, -8)
    bot_window.show()
    bot_window.activate()
    
    (width, height) = pyautogui.size() 
    bot_window.resizeTo(width + 16, height - 14) 

    await asyncio.sleep(2)
    

def get_action_index_by_window(bot_name: str, window):

    for i in range(0,  len(all_actions[bot_name])):
        if all_actions[bot_name][i]["window"] == window:
            return i

    raise Exception("Couldn't find the the index for the window")


def write_next_actions_sumary(next_actions: List[Prodict]):

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
    next_action_schedule_sec = add_extra_wait_time_during_dawn(next_action, next_action_schedule_sec)

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


def add_extra_wait_time_during_dawn(next_action: Prodict, next_action_schedule_sec):
    if 'parameters' in next_action.config:
        if 'extra_wait_time_during_dawn_sec' in next_action.config.parameters:
            
            dt = datetime.now()
            if dt.hour >= 0 and dt.hour <= 6:
                next_action_schedule_sec += next_action.config.parameters.extra_wait_time_during_dawn_sec

    return next_action_schedule_sec


def get_next_actions():
    actions = []
    for key in all_actions:
        actions = actions + all_actions[key]

    next_actions = sorted(actions,
                            key=lambda a: min(a['schedules'].items(), key=lambda x: x[1])[1],
                            reverse=False)

    return next_actions


while(True):
    try:    

        asyncio.run(main())

    except:
        traceback.print_exc()
        last_window_amount_by_bot = Prodict({})
        all_actions = Prodict({})

