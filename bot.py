# Importa a biblioteca de threading
import threading
from ImageProcessing import ImageProcessor
from Input import InputController
from wc import WindowCapture
import cv2 as cv
import time
import winsound


class Bot:
    def __init__(self):
        self.controller = InputController()
        self.imageProcessor = ImageProcessor()
        self.gameScreen = WindowCapture()

        self.is_fishing = False
        self.latest_screenshot = None
        self.screenshot_lock = threading.Lock()

        # Variáveis não utilizadas por enquanto, mas mantidas
        self.last_fish_detection = time.time()
        self.last_move_time = time.time()
        self.fish_detection_delay_range = (10, 15)

        # Carregamento de templates (código omitido por brevidade, mas está correto)
        self.numbers_templates = {
            "1": cv.imread("./templates/Notifications/Numbers/1.png"),
            "2": cv.imread("./templates/Notifications/Numbers/2.png"), 
            "3": cv.imread("./templates/Notifications/Numbers/3.png"), 
            "4": cv.imread("./templates/Notifications/Numbers/4.png"), 
            "5": cv.imread("./templates/Notifications/Numbers/5.png"), 
            "6": cv.imread("./templates/Notifications/Numbers/6.png"), 
            "7": cv.imread("./templates/Notifications/Numbers/7.png"), 
            "8": cv.imread("./templates/Notifications/Numbers/8.png"),
            }
        
        self.backspace_template = cv.imread("./templates/Notifications/BACKSPACE.png")
        self.fishing_rod_button_template = cv.imread("./templates/F2/vara.png")
        self.use_button_template = cv.imread("./templates/F2/usar.png")
        self.baitlvl1_button_template = cv.imread("./templates/F2/lvl1.png")
        self.inventario_button_template = cv.imread("./templates/F2/inventario.png")
        self.voltar_button_template = cv.imread("./templates/F2/voltar.png")
        
        screenshot_thread = threading.Thread(target=self._screenshot_loop, daemon=True)
        screenshot_thread.start()

        status_thread = threading.Thread(target=self._update_fishing_status_loop, daemon=True)
        status_thread.start()

    def _screenshot_loop(self):
        while True:
            screenshot = self.gameScreen.get_screenshot()
            with self.screenshot_lock:
                self.latest_screenshot = screenshot
            time.sleep(1/60)

    ### CORREÇÃO ###
    # Nova função auxiliar para pegar a tela de forma segura
    def _get_current_screen(self):
        """ Pega uma cópia segura e atual da tela. """
        # Espera até que o primeiro screenshot esteja disponível
        while self.latest_screenshot is None:
            time.sleep(0.1)
        
        with self.screenshot_lock:
            return self.latest_screenshot.copy()

    def _update_fishing_status_loop(self):
        FISHING_STATUS_AREA = [30, 680, 270, 360]
        while True:
            current_screen = self._get_current_screen()
            if self.has_image_on_screen(current_screen, self.backspace_template, False, FISHING_STATUS_AREA):
                self.is_fishing = True
            else:
                self.is_fishing = False
            time.sleep(1)

    def beep(self, frequency=200, duration=100):
        winsound.Beep(frequency, duration)
    
    def has_image_on_screen(self, game_img_base, image_template, greenMask=False, area=None):
        game_img = game_img_base.copy()
        if area:
            game_img = self.imageProcessor.crop_image(game_img, area[0], area[1], area[2], area[3])
        if greenMask:
            game_img = self.imageProcessor.apply_green_mask(game_img)
        pos, accuracy = self.imageProcessor.template_matching(game_img, image_template)
        if accuracy > 90:
            return pos
        return False
    
    def check_if_is_fishing(self):
        print(f"Verificando status: {'Pescando' if self.is_fishing else 'Não está pescando'}")
        return self.is_fishing

    ### CORREÇÃO ###
    # Corrigido o nome da função
    def waiting_fish(self):
        FISHING_MINIGAME_AREA = [30, 680, 270, 360]
        while self.is_fishing:
            current_screen = self._get_current_screen()
            for index, template in self.numbers_templates.items():
                processed_template = self.imageProcessor.apply_green_mask(template)
                if self.has_image_on_screen(current_screen, processed_template, True, FISHING_MINIGAME_AREA):
                    self.controller.pressKey(index)
                    self.beep()
            time.sleep(0.05)

    ### CORREÇÃO ###
    # Lógica de `use_item` completamente refeita para usar screenshots atualizados
    def use_item(self, itemTemplate):
        # Verifica se precisa clicar em "Voltar"
        screen = self._get_current_screen()
        voltar_pos = self.has_image_on_screen(screen, self.voltar_button_template)
        if voltar_pos:
            self.controller.mouseClick(voltar_pos)
            time.sleep(2)

        # Verifica se o inventário está aberto. Pega uma nova tela caso tenha clicado em "Voltar"
        screen = self._get_current_screen()
        if not self.has_image_on_screen(screen, self.inventario_button_template):
            print("Abrindo inventário...")
            self.controller.pressKey("f2")
            time.sleep(2)

        # Procura o item. Pega uma nova tela, pois o inventário pode ter sido aberto.
        screen = self._get_current_screen()
        item_pos = self.has_image_on_screen(screen, itemTemplate)
        if not item_pos:
            print("Item não encontrado no inventário.")
            print("Fechando inventário.")
            self.controller.pressKey("backspace")
            return
        
        # Clica no item
        self.controller.mouseClick(item_pos)
        time.sleep(2)

        # Procura o botão "Usar". Pega uma nova tela após clicar no item.
        screen = self._get_current_screen()
        use_button_pos = self.has_image_on_screen(screen, self.use_button_template)
        if use_button_pos:
            self.controller.mouseClick(use_button_pos)
            time.sleep(2)
        else:
            print("Botão 'Usar' não encontrado após clicar no item.")

    def start_fishing(self):
        if self.is_fishing:
            return

        self.use_item(self.baitlvl1_button_template)
        time.sleep(3) # Pequena pausa entre usar a isca e a vara
        self.use_item(self.fishing_rod_button_template)

        time.sleep(5) # Espera a animação de pesca começar
        
        # Verifica se a pescaria realmente começou antes de entrar no loop
        if self.is_fishing:
            self.waiting_fish()
        else:
            print("A pescaria não foi iniciada. Tentando novamente no próximo ciclo.")

    def start_burning_mode(self):
        pass

    def move(self):
        self.last_move_time = time.time()

        self.controller.keyboard.press("a")
        time.sleep(3)
        self.controller.keyboard.release("a")
        self.controller.keyboard.press("d")
        time.sleep(3)
        self.controller.keyboard.release("d")


if __name__ == "__main__":
    print("Iniciando o bot em 3 segundos...")
    time.sleep(3)
    bot = Bot()
    while True:
        if not bot.is_fishing:
            if time.time() - bot.last_move_time > 400:
                bot.move()
            bot.start_fishing()

        time.sleep(5)