from pynput.keyboard import Controller
from pynput.mouse import Controller as MouseController
import threading
import time

class InputController:
    def __init__(self):
        self.keyboard = Controller()
        self.pressed_keys = set()  # Armazena as teclas atualmente pressionadas
        self.lock = threading.Lock()  # Para thread safety
    
    def pressNum(self, num, delay, release_delay):
        # Verifica se a tecla já está pressionada (thread safe)
        with self.lock:
            if num in self.pressed_keys:
                return  # Despreza se já estiver pressionada
            
            # Adiciona à lista de teclas pressionadas
            self.pressed_keys.add(num)
        
        # Cria e inicia thread para executar o press/release
        thread = threading.Thread(target=self._execute_key_press, args=(num, delay, release_delay))
        thread.daemon = True  # Thread será finalizada quando o programa principal terminar
        thread.start()
    
    def _execute_key_press(self, num, delay, release_Delay):
        """Método privado que executa o press/release em thread separada"""
        try:
            # Aguarda o delay
            time.sleep(delay)

            # Pressiona a tecla
            self.keyboard.press(num)
            print(num + " foi pressionado")
            
            # Aguarda o delay
            time.sleep(release_Delay)
            
            # Libera a tecla
            self.keyboard.release(num)
            print(num + " foi liberado")
            
        finally:
            # Remove da lista de teclas pressionadas (thread safe)
            with self.lock:
                self.pressed_keys.discard(num)  # discard não gera erro se não existir
    
    def get_pressed_keys(self):
        """Retorna as teclas atualmente pressionadas"""
        with self.lock:
            return self.pressed_keys.copy()
    
    def is_key_pressed(self, num):
        """Verifica se uma tecla específica está pressionada"""
        with self.lock:
            return num in self.pressed_keys