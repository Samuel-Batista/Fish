import threading
# Remova as importações não utilizadas se houver
# from ImageProcessing import ImageProcessor
# from Input import InputController
# from wc import WindowCapture
import cv2 as cv
import time
import winsound

# Supondo que essas classes existam nos seus outros arquivos
class ImageProcessor:
    def crop_image(self, img, x, y, w, h): pass
    def apply_green_mask(self, img): pass
    def template_matching(self, img, template): return (None, 0)

class InputController:
    def pressKey(self, key): pass
    def mouseClick(self, pos): pass

class WindowCapture:
    def get_screenshot(self): return None # Retorna um objeto de imagem

class Bot:
    def __init__(self):
        self.controller = InputController()
        self.imageProcessor = ImageProcessor()
        self.gameScreen = WindowCapture()

        self.is_fishing = False
        
        ### MUDANÇA ###
        # Atributo para armazenar a imagem mais recente da tela
        self.latest_screenshot = None
        # Lock para garantir que não lemos o screenshot enquanto ele está sendo escrito
        self.screenshot_lock = threading.Lock()

        # Carrega os templates
        # (Seu código de carregar templates aqui, omitido por brevidade)
        self.numbers_templates = {} # Preencha como antes
        self.backspace_template = cv.imread("./templates/Notifications/BACKSPACE.png")
        # ... etc

        ### MUDANÇA ###
        # Inicia a thread que vai ATUALIZAR A TELA
        screenshot_thread = threading.Thread(target=self._screenshot_loop, daemon=True)
        screenshot_thread.start()

        # Inicia a thread que vai monitorar o status da pesca
        status_thread = threading.Thread(target=self._update_fishing_status_loop, daemon=True)
        status_thread.start()

    ### MUDANÇA ###
    # Nova thread dedicada a capturar a tela
    def _screenshot_loop(self):
        """
        Roda em uma thread separada, continuamente capturando a tela do jogo
        e armazenando na variável self.latest_screenshot.
        """
        while True:
            screenshot = self.gameScreen.get_screenshot()
            with self.screenshot_lock:
                self.latest_screenshot = screenshot
            # Captura a ~30 FPS. Ajuste se necessário.
            time.sleep(1/30) 

    def _update_fishing_status_loop(self):
        """
        Verifica continuamente se o jogador está pescando.
        Agora usa a imagem já capturada pela outra thread.
        """
        FISHING_STATUS_AREA = [30, 680, 270, 360]
        while True:
            # Espera até que o primeiro screenshot seja feito
            if self.latest_screenshot is None:
                time.sleep(0.5)
                continue

            with self.screenshot_lock:
                # Faz uma cópia para não segurar o lock durante o processamento
                current_screen = self.latest_screenshot.copy()

            # ### MUDANÇA ###: Passa a imagem para a função
            if self.has_image_on_screen(current_screen, self.backspace_template, 5, False, FISHING_STATUS_AREA):
                self.is_fishing = True
            else:
                self.is_fishing = False
            
            time.sleep(1)

    def beep(self, frequency=200, duration=100):
        winsound.Beep(frequency, duration)
    
    ### MUDANÇA ###
    # A função agora recebe a imagem da tela como primeiro argumento
    def has_image_on_screen(self, game_img_base, image_template, greenMask=False, area=None):
        """
        Verifica se uma imagem (template) está presente em uma imagem base.
        """
        # Não precisamos mais de um loop aqui, pois a imagem já é um "instantâneo"
        # O loop de tentativas pode ser removido para simplificar, ou mantido se a detecção for instável.
        # Para este exemplo, vamos simplificar e fazer uma única verificação precisa.
        
        game_img = game_img_base.copy() # Trabalha com uma cópia

        if area:
            game_img = self.imageProcessor.crop_image(game_img, area[0], area[1], area[2], area[3])

        if greenMask:
            game_img = self.imageProcessor.apply_green_mask(game_img)

        pos, accuracy = self.imageProcessor.template_matching(game_img, image_template)

        if accuracy > 90:
            return pos
        
        return False

    # ... (check_if_is_fishing permanece igual) ...

    def waiting_fish(self):
        FISHING_MINIGAME_AREA = [30, 680, 270, 360]
        while self.is_fishing:
            if self.latest_screenshot is None:
                time.sleep(0.1)
                continue
            
            with self.screenshot_lock:
                current_screen = self.latest_screenshot.copy()

            for index, template in self.numbers_templates.items():
                processed_template = self.imageProcessor.apply_green_mask(template)
                # ### MUDANÇA ###: Passa a imagem atual para a função
                if self.has_image_on_screen(current_screen, processed_template, 1, True, FISHING_MINIGAME_AREA):
                    self.controller.pressKey(index)
                    self.beep()
            
            time.sleep(0.05)

    # ... (use_item e start_fishing precisarão de ajustes similares para usar self.latest_screenshot) ...
    # Exemplo para use_item:
    def use_item(self, itemTemplate):
        with self.screenshot_lock:
            current_screen = self.latest_screenshot.copy()
        
        # ### MUDANÇA ###: Passa a imagem para a função
        voltar_pos = self.has_image_on_screen(current_screen, self.voltar_button_template, 10)
        # ... e assim por diante para todas as chamadas de has_image_on_screen ...


# O loop principal (__main__) não precisa de mudanças.