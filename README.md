# TOB - The Only Bot
## A completely FREE, OPENSOURCE game bot orchestrator.
- TOB is lightweight and easily runs multiple bots, for multiple accounts, multiple games, multiple windows with a few configurations
- You can run as many windows as your computer can handle
- Supported Games
  - BombCrypto (scholar included)
  - LunaRush
  - Space Crypto (Any number of ships)
  - AgroFarm
  - CryptoPiece (4 heroes)
  - Want another game? Lets talk about it: flaviodiasps@gmail.com

## TOB works through image recognition and by simulating mouse movimentation/clicks
- TOB won't ask any information
- TOB won't read your personal data
- TOB won't save anything anywhere
- TOB won't connect to the internet
- TOB won't do any transaction

# Notes
- For technical reasons, **TOB only works on computers running windows**, even though it is made in python =(
- Every file is readable and you can open with notepad, vscode or any other text editor.
- **TOB only works with an english metamask**
- You can open as many accounts / windows your computer can handle
- It is better if you don't use the computer while the bot is running. You might disturb it by moving your mouse.
- If you want to use the computer while the bot is running you have a few options
  - If the game that is running has high wait durations, you can use it as long as the bot is not trying to use
  - If you want to use the cocmputer at any time, check this tool: https://www.ibik.ru/ It is not free, but solves the problem
  - If you want a free option and has lots of computer power, try virtual machines using softwares like VMware. You can run the bot there too


# CONTRIBUTION
## Belive me, I am not rich.
If TOB is helping you saving lots of time time, few free to donate the value you think it is fair for my work: 
- METAMASK BSC: 0x12198f741eddF0dB5450E16bA197027492bC9f98
- PIX: d9298453-6fa2-4c24-969b-c9027666cb5e


# How to SETUP
## Installing TOB requirements
1. Download this project
2. Install python 3.9.9 (MARK THE OPTION THAT ADDS VARIABLE TO WINDOWS PATH): https://www.python.org/downloads/release/python-399/
3. Double-Click in install.bat file. This will install the project dependencies.
4. Open your browser (It was tested only on chrome and brave)
5. Install metamask extension (put it in english)
6. Go to the game website, example: https://app.bombcrypto.io/
7. Right-Click on the top of the window (not in the tab, in the window). It will show a rename option in the menu. Rename it to tob_"GameName". Example: tob_bombcrypto. If you have multiple windows for the same game you can add anything to the name. Example: "1 - tob_bombcrypto", "my tob_bombcrypto 2". Windows will run in lexicographic order.
8. **You must ZOOM OUT the window to 67% zoom. This is the best way I found to fit more windows in the same monitor (cryptopiece is an exception, it has to be 50%)**
9. **If the game has the option to decrease graphic quality, you must put it in the lowest possible, like it is in LunaRush otherwise TOB won't work** 
10. If you have multiple windows, organize them in a way they don't complete overlapp the other. **They can be at almost 100% overlapping, but some games stop if they are completely blocked by another window or minimized**
11. All necessary stuff is configured, but bo won't work yet. Every game might have a different need. Lets configure them.

## Configuring games
### config.yaml
1. The config.yaml file might look like this:
`
tob:
  press_space_before_and_after_bot: False

spacecrypto:
  window_name: tob_spacecrypto
  parameters:
    spaceship_scroll_limit: 3
  intervals:
    wait_for_surrender_sec: 310
    time_to_speed_victory_sec: 10
`
These are different configurations for each game, so you can customize a few things. 
Example: "wait_for_surrender_sec"= Duration in seconds that each window will wait before surrendering.
**TOB might not run it in a precise time. If another game bot is running at the time a specific window should run, this window will have to wait until the game bot ends**

## Games configuration
### BombCrypto
- ZOOM: 67%
- WINDOW NAME: tob_bombcrypto
- send_heroes_to_work_sec: Seconds to wait before calling the bot to send new heroes to work
- refresh_heroes_positions_sec: Seconds to wait before calling the bot to refresh heroes positions
### LunaRush
- ZOOM: 67%
- WINDOW NAME: tob_lunarush
- Graphic Quality: Low
- extra_wait_time_during_dawn_sec: Removed
- battle_not_ended_max_retries: Amount of times the bot will check the bot to see if battle has ended before throwing an error
- wait_for_battle_sec: Amount of secongs to wait for the end of battle
- wait_for_energy_sec: Seconds to wait for energy recovery
- battle_not_ended_yet_sec: Extra seconds to wait in the case the battle is still happening 
### SpaceCrypto
- ZOOM: 67%
- WINDOW NAME: tob_spacecrypto
- spaceship_scroll_limit: Amount of times that it will scroll down to search for new spaceships with available energy
- wait_for_surrender_sec: Seconds to wait before surrendering
- time_to_speed_victory_sec: Seconds to wait before checking if there is a victory button to click
### CryptoPiece
- ZOOM: 50%
- WINDOW NAME: tob_cryptopiece
- **Only works for accounts with 4 characters**
- wait_for_stamina_sec: Seconds to wait for stamina recovery
### AgroFarm
- ZOOM: 67%
- WINDOW NAME: tob_agrofarm
- wait_time_when_no_crop_left_sec: Seconds to wait for new crops to farm

FAQ
# I click start but the terminal window closes instantly
- You probably didn't install dependencies
- You probably didn't add python variable in the path during install setup

# TOB opens but stops asking me to rename all windows
- You must rename the window of the game to the correct name. For bombcrypto would be "anything you want here"tob_bombcrypto"anything you want here"
- Do not rename all windows with the same name, TOB will get confused and behave unexpectedly 

# TOB is not signing in to my metamask
- Check if your metamask in english
- Make sure Metamask is not asking for you password. (TOB needs that you leave your metamask logged)

# TOB is running but not working properly in the game
- Make sure window zoom is correct
- Read the error message, it might help figure out what happened.
- If TOB is still not working,  it might not be recognizing the images in you monitor
  - Go to the templates folder. There is a folder for each game.
  - There you can see all the pictures that the game bot will try to recognize. 
  - Replace them, so the bot can recognize as it is in your computer.

