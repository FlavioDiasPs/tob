import os
import pygetwindow
import traceback
import asyncio
import copy


from prodict import Prodict
from datetime import datetime
from helpers.printfier import Printer
from runner import Runner

p = Printer(bot_name='TOB')


async def run_action(runner: Runner):

    p.info('Taking bot windows')
    next_action = runner.next_action
    bot_windows = get_bot_windows(next_action.config.window_name)

    bot_name_not_in_the_previous_window_list = not (next_action.bot_name in runner.last_window_amount_by_bot)

    if (bot_name_not_in_the_previous_window_list or runner.last_window_amount_by_bot[next_action.bot_name] != len(bot_windows)):
        runner.all_actions[next_action.bot_name] = await run_all_actions(bot_windows, next_action)

    else:
        result = await run_single_action(next_action)
        index = get_action_index_by_window(runner.all_actions, next_action.bot_name, result.window)
        runner.all_actions[next_action.bot_name][index] = result

    runner.last_window_amount_by_bot[next_action.bot_name] = len(bot_windows)


def get_bot_windows(window_name: str):
    amount_windows = 0
    while(amount_windows <= 0):
        windows = pygetwindow.getWindowsWithTitle(window_name)
        amount_windows = len(windows)

        if amount_windows <= 0:
            print(f"Rename all the windows to: {window_name}")
            os.system("pause")

    return windows


def get_action_index_by_window(all_actions: Prodict,  bot_name: str, window):

    for i in range(0, len(all_actions[bot_name])):
        if all_actions[bot_name][i]["window"] == window:
            return i

    raise Exception("Couldn't find the the index for the window")


async def run_single_action(next_action: Prodict):
    p.info('Running action')
    return await wrap_bot_function(next_action)


async def run_all_actions(bot_windows, next_action: Prodict):
    result_actions = []  

    p.info('Running action') 
    for bot_window in bot_windows:

        aux_next_action = Prodict(copy.deepcopy(next_action))
        aux_next_action.window = bot_window

        result_action = Prodict(await wrap_bot_function(aux_next_action))
        result_actions.append(result_action)

    return result_actions


async def wrap_bot_function(next_action: Prodict):
    retry_count = 0
    retry_limit = 5
    retry_schedule_name = f'retry_failed_{next_action.bot_name}'

    bot_function = next_action.function
    
    while(retry_count <= retry_limit):
        try:

            if retry_schedule_name in next_action.schedules:
                next_action.schedules = Prodict({})

            return await bot_function(next_action)

        except:
            traceback.print_exc()
            await asyncio.sleep(2)
            retry_count += 1

    now = datetime.timestamp(datetime.now())
    next_action.schedules = Prodict({})
    next_action.schedules[retry_schedule_name] = now + 30 * 60

    return next_action