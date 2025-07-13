from pynput.keyboard import Controller, Key as ALL_KELLS
from pynput import keyboard
from time import sleep, time

controller = Controller()
pause = True
move_time = time()

DEFALT_DELAY = 0.1
ITEM_INDEX = 1
DUP_AMMOUNT = 2
DEPOSIT_AMMOUNT = DUP_AMMOUNT * 2

def pres(key, hold_duration=None):
    controller.press(key)
    if key == ALL_KELLS.enter:
        sleep(0.2)
    elif key == ALL_KELLS.backspace:
        sleep(0.05)
    elif key == ALL_KELLS.up:
        sleep(0.05)
    else:
        sleep(DEFALT_DELAY)

    controller.release(key)

def toggle_pause():
    global pause
    pause = not pause
    print(f"Pause: {pause}")


def ant_afk():
    global move_time

    move_time = time()
    pres("f")
    sleep(5)
    pres("f")

    

# Cria um hotkey global para a tecla 'p'f
hotkey = keyboard.GlobalHotKeys({
    'u': toggle_pause
})

# Inicia o hotkey listener em thread separada
hotkey.start()

sleep(3)
ant_afk()

while True:
    sleep(1)
    if time() - move_time > 5*60:
        ant_afk()