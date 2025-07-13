from pynput.keyboard import Controller, Key as ALL_KELLS
from pynput import keyboard
from time import sleep
import pyautogui

pause = True  # Inicializa a variável pause

def toggle_pause():
    global pause
    pause = not pause
    print(f"Pause: {pause}")

# Cria um hotkey global para a tecla 'u'
hotkey = keyboard.GlobalHotKeys({
    'i': toggle_pause
})

# Inicia o hotkey listener em thread separada
hotkey.start()

screenshot_count = 0

while True:
    sleep(1)
    if pause:
        continue

    # Captura a tela 1 (monitor primário)
    screenshot = pyautogui.screenshot()
    screenshot.save(f"./print/screenshot_{screenshot_count}.png")
    screenshot_count += 1