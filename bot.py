# Importa a biblioteca de threading
import threading
from ImageProcessing import ImageProcessor
from Input import InputController
from wc import WindowCapture
import cv2 as cv
import time
import winsound
import numpy as np
import random
import os


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        img = cv.imread(file_path)
        if img is not None:
            images.append(img)
    return images



class Bot:
    def __init__(self):
        self.controller = InputController()
        self.imageProcessor = ImageProcessor()
        self.gameScreen = WindowCapture()

        self.pescando = False
        self.fish_detected = False
        self.latest_screenshot = None
        self.screenshot_lock = threading.Lock()

        # Variáveis não utilizadas por enquanto, mas mantidas
        self.last_fish_detection = time.time()
        self.last_move_time = time.time()
        self.fish_detection_delay_range = (10, 15)

        self.keys_templates = {
            "w": load_images_from_folder("./templates/keys/W"),
            "a": load_images_from_folder("./templates/keys/A"),
            "s": load_images_from_folder("./templates/keys/S"),
            "d": load_images_from_folder("./templates/keys/D"),
        }

        self.peixes_discarte = [
            "tilapia",
            "saicanga", 
            "traira", 
            "piaucu", 
            "tambaqui", 
            "pacu", 
            "achiga", 
            "cachorra", 
            "corvina", 
            "bicuda"
        ]

        self.peixes = {
            "tilapia" : {
                "template":cv.imread("./templates/peixes/tilapia.png"),
                "peso":3,
                "valor":600
            },
            "saicanga" : {
                "template":cv.imread("./templates/peixes/saicanga.png"),
                "peso":5,
                "valor":600
            },
            "traira" : {
                "template":cv.imread("./templates/peixes/traira.png"),
                "peso":4,
                "valor":600
            },
            "piaucu" : {
                "template":cv.imread("./templates/peixes/piaucu.png"),
                "peso":3,
                "valor":600
            },
            "tambaqui" : {
                "template":cv.imread("./templates/peixes/tambaqui.png"),
                "peso":5,
                "valor":600
            },
            "pacu" : {
                "template":cv.imread("./templates/peixes/pacu.png"),
                "peso":8,
                "valor":600
            },
            "achiga" : {
                "template":cv.imread("./templates/peixes/achiga.png"),
                "peso":3,
                "valor":600
            },
            "cachorra" : {
                "template":cv.imread("./templates/peixes/cachorra.png"),
                "peso":4,
                "valor":600
            },
            "corvina" : {
                "template":cv.imread("./templates/peixes/corvina.png"),
                "peso":5,
                "valor":600
            },
            "bicuda" : {
                "template":cv.imread("./templates/peixes/bicuda.png"),
                "peso":8,
                "valor":600
            },
            "pirarara" : {
                "template":cv.imread("./templates/peixes/pirarara.png"),
                "peso":3,
                "valor":600
            },
            "dourado" : {
                "template":cv.imread("./templates/peixes/dourado.png"),
                "peso":4,
                "valor":600
            },
            "pirarucu" : {
                "template":cv.imread("./templates/peixes/pirarucu.png"),
                "peso":5,
                "valor":600
            },
            "pintado" : {
                "template":cv.imread("./templates/peixes/pintado.png"),
                "peso":10,
                "valor":600
            },
            "tucunare" : {
                "template":cv.imread("./templates/peixes/tucunare.png"),
                "peso":3,
                "valor":600
            },
            "tartaruga" : {
                "template":cv.imread("./templates/peixes/tartaruga.png"),
                "peso":5,
                "valor":600
            },
            "peixeboi" : {
                "template":cv.imread("./templates/peixes/peixeboi.png"),
                "peso":10,
                "valor":600
            },
            "jacare" : {
                "template":cv.imread("./templates/peixes/jacare.png"),
                "peso":10,
                "valor":600
            },
        }
        
        
        self.fishing_rod_button_template = cv.imread("./templates/F2/vara.png")
        self.use_button_template = cv.imread("./templates/F2/usar.png")
        self.inventario_button_template = cv.imread("./templates/F2/inventario.png")
        self.voltar_button_template = cv.imread("./templates/F2/voltar.png")
        self.jogar_fora_template = cv.imread("./templates/F2/jogarFora.png")
        self.quantidade_template = cv.imread("./templates/F2/quantidade.png")
        self.confirmar_template = cv.imread("./templates/F2/confirmar.png")

        self.ancora_template = cv.imread("./templates/ancora.png")
        self.isca0_template = cv.imread("./templates/isca0.png")
        self.isca3_template = cv.imread("./templates/isca3.png")

        self.pescando_notification = cv.imread("./templates/PESCAR.png")
        
        screenshot_thread = threading.Thread(target=self._screenshot_loop, daemon=True)
        screenshot_thread.start()

        pescando_thread = threading.Thread(target=self._update_pescando_loop, daemon=True)
        pescando_thread.start()

        fish_detect_thread = threading.Thread(target=self._update_fish_detected_loop, daemon=True)
        fish_detect_thread.start()

        minigame_thread = threading.Thread(target=self.mini_game_loop, daemon=True)
        minigame_thread.start()


    def _screenshot_loop(self):
        while True:
            screenshot = self.gameScreen.get_screenshot()
            with self.screenshot_lock:
                self.latest_screenshot = screenshot
            time.sleep(1/30)

    def _get_current_screen(self):
        """ Pega uma cópia segura e atual da tela. """
        # Espera até que o primeiro screenshot esteja disponível
        while self.latest_screenshot is None:
            time.sleep(0.1)
        
        with self.screenshot_lock:
            return self.latest_screenshot.copy()

    def _update_pescando_loop(self):
        FISHING_STATUS_AREA = [1040, 940, 150, 70]
        
        def has_image():
            current_screen = self._get_current_screen()
            pescando_notication_image_area = self.imageProcessor.crop_image(current_screen, FISHING_STATUS_AREA[0], FISHING_STATUS_AREA[1], FISHING_STATUS_AREA[2], FISHING_STATUS_AREA[3])
            if self.has_image_on_screen(pescando_notication_image_area, self.pescando_notification):
                return True
            return False
            
        while True:
            
            if has_image() and not self.pescando:
                valid = True
                for _ in range(10):
                    time.sleep(0.1)
                    print("cheking pescando")
                    if not has_image():
                        valid = False
                        break
                if valid:
                    self.pescando = True

            elif not has_image() and self.pescando:
                valid = True
                for _ in range(10):
                    time.sleep(0.1)
                    print("cheking NOT pescando")
                    if has_image():
                        valid = False
                        break
                if valid:
                    self.pescando = False
            

            # print(self.pescando)
            time.sleep(1)

            # cv.imshow("notificationPreview", pescando_notication_image_area)
            # cv.waitKey(1)

    def _update_fish_detected_loop(self):
        BAR_AREA = [1658, 385, 35, 300]

        def get_bar_percent():
            game_screen = self._get_current_screen()
            bar_screen_image_area = self.imageProcessor.crop_image(game_screen, BAR_AREA[0], BAR_AREA[1], BAR_AREA[2], BAR_AREA[3])
            bar_mask = self.imageProcessor.create_color_mask(bar_screen_image_area, np.array([65, 200, 150]), np.array([85, 255, 255]))
            bar_percent = self.imageProcessor.colored_pixels_percentage(bar_mask)

            return bar_percent

        while True:
            bar_percent = get_bar_percent()

            if bar_percent >= 5 and not self.fish_detected:
                valid = True
                """check 10 times fast to verify"""
                for _ in range(10):
                    time.sleep(0.1)
                    print("cheking HAS BAR")
                    if get_bar_percent() < 5:
                        valid = False
                        break

                if valid:
                    self.fish_detected = True


            elif bar_percent < 5 and self.fish_detected:
                valid = True
                """check 10 times fast to verify"""
                for _ in range(10):
                    time.sleep(0.1)
                    print("cheking NOT HAS BAR")
                    if get_bar_percent() >= 5:
                        valid = False
                        break

                if valid:
                    self.fish_detected = False

            time.sleep(0.3)

    def beep(self, frequency=200, duration=100):
        winsound.Beep(frequency, duration)
    
    def has_image_on_screen(self, game_img_base, image_template, mask=None, area=None):
        """
        Verifica se uma imagem está presente na tela, podendo aplicar uma máscara.

        Args:
            game_img_base: Imagem base da tela
            image_template: Template a ser procurado
            mask: Máscara binária (opcional, numpy array)
            area: Área específica para procurar [x, y, width, height]
        """
        game_img = game_img_base.copy()
        if area:
            game_img = self.imageProcessor.crop_image(game_img, area[0], area[1], area[2], area[3])
            if mask is not None:
                mask = self.imageProcessor.crop_image(mask, area[0], area[1], area[2], area[3])
        if mask is not None:
            game_img = self.imageProcessor.apply_mask(game_img, mask)
        pos, accuracy = self.imageProcessor.template_matching(game_img, image_template)
        if accuracy > 90:
            return pos
        return False

    def wait_for_image(self, image_template, timeout=10, area=None, mask=None):
        """
        Espera até que uma imagem apareça na tela, com um tempo limite.
        Retorna a posição da imagem se encontrada, ou False se o tempo esgotar.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            screen = self._get_current_screen()
            pos = self.has_image_on_screen(screen, image_template, mask=mask, area=area)
            if pos:
                return pos
            time.sleep(0.2)
        print(f"Timeout! Imagem não encontrada em {timeout} segundos.")
        return False
    
    def check_if_is_fishing(self):
        print(f"Verificando status: {'Pescando' if self.is_fishing else 'Não está pescando'}")
        return self.is_fishing

    def get_key(self):
        MINI_GAME_AREA = [1690, 400, 210, 300]
        game_scren = self._get_current_screen()
        mini_game_image_area = self.imageProcessor.crop_image(game_scren, MINI_GAME_AREA[0], MINI_GAME_AREA[1], MINI_GAME_AREA[2], MINI_GAME_AREA[3])
        
        for key, templates in self.keys_templates.items():
            ramdom_template = templates[random.randint(0, len(templates)-1)]
            if self.has_image_on_screen(mini_game_image_area, ramdom_template):
                return key

        return False
        # cv.imshow("minigame_preview", mini_game_image_area)
        # cv.waitKey(1)

    def mini_game_loop(self):
        while True:
            current_key = self.get_key()
            if current_key:
                self.controller.pressKey(current_key)

            time.sleep(1/30)

    def jogar_fora(self, item_template):
        self.abrir_inventario()
        screen = self._get_current_screen()

    def discarte_peixes(self):
        for peixe_name in self.peixes_discarte:
            peixe_template = self.peixes[peixe_name]["template"]
            self.abrir_inventario()
            screen = self._get_current_screen()
            peixe_pos = self.has_image_on_screen(screen, peixe_template)
            if peixe_pos:
                print("peixe ruim detectado, jogando fora ...")
                self.controller.mouseClick(peixe_pos)
                jogar_fora_pos = self.wait_for_image(self.jogar_fora_template)
                self.controller.mouseClick(jogar_fora_pos)
                quantidade_pos = self.wait_for_image(self.quantidade_template)
                self.controller.mouseClick(quantidade_pos)
                time.sleep(0.1)
                self.controller.pressKey("1")
                time.sleep(0.1)
                confirmar_pos = self.wait_for_image(self.confirmar_template)
                self.controller.mouseClick(confirmar_pos)
                time.sleep(0.2)
                break
           
    def abrir_inventario(self):
        # Verifica se precisa clicar em "Voltar"
        screen = self._get_current_screen()
        voltar_pos = self.has_image_on_screen(screen, self.voltar_button_template)
        if voltar_pos:
            self.controller.mouseClick(voltar_pos)
            self.wait_for_image(self.inventario_button_template)

        # Verifica se o inventário está aberto. Pega uma nova tela caso tenha clicado em "Voltar"
        screen = self._get_current_screen()
        if not self.has_image_on_screen(screen, self.inventario_button_template):
            print("Abrindo inventário...")
            self.controller.pressKey("f2")
            self.wait_for_image(self.inventario_button_template)
    
    def use_item(self, itemTemplate):
       # abre o inventario
        self.abrir_inventario()

        # Procura o item. Pega uma nova tela, pois o inventário pode ter sido aberto.
        screen = self._get_current_screen()
        item_pos = self.wait_for_image(itemTemplate)
        if not item_pos:
            print("Item não encontrado no inventário.")
            print("Fechando inventário.")
            self.controller.pressKey("backspace")
            return
        
        # Clica no item
        self.controller.mouseClick(item_pos)
        
        # Procura o botão "Usar". Pega uma nova tela após clicar no item.
        screen = self._get_current_screen()
        use_button_pos = self.wait_for_image(self.use_button_template)
        if use_button_pos:
            self.controller.mouseClick(use_button_pos)
            time.sleep(1)
        else:
            print("Botão 'Usar' não encontrado após clicar no item.")

    def start_fishing(self):
        if self.pescando:
            return

        self.use_item(self.fishing_rod_button_template)
        isca_pos = self.wait_for_image(self.isca3_template)
        if isca_pos:
            self.controller.mouseClick(isca_pos)

        time.sleep(5) # Espera a animação de pesca começar

    def ant_afk(self):
        self.last_move_time = time.time()
        self.controller.keyboard.press("f")
        time.sleep(0.15)
        self.controller.keyboard.release("f")
        time.sleep(15)
        self.controller.keyboard.press("f")
        time.sleep(0.15)
        self.controller.keyboard.release("f")
        time.sleep(5)
        self.use_item(self.ancora_template)
        time.sleep(5)


if __name__ == "__main__":
    from pynput import keyboard
    pause = True  # Inicializa a variável pause

    def toggle_pause():
        global pause
        pause = not pause
        print(f"Pause: {pause}")

    # Cria um hotkey global para a tecla 'u'i
    hotkey = keyboard.GlobalHotKeys({
        'i': toggle_pause
    })

    hotkey.start()

    bot = Bot()

    while True:
        if pause:
            time.sleep(1)
            bot.last_move_time = time.time()
            continue

        if not bot.pescando:
            if time.time() - bot.last_move_time > 10*60:
                bot.ant_afk()
            bot.discarte_peixes()
            bot.start_fishing()

        # key_ = bot.get_key()
        # if key_:
        #     bot.controller.pressKey(key=key_)

        time.sleep(1/30)