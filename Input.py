from pynput.keyboard import Controller, Key as ALL_KELLS
from pynput.mouse import Controller as MouseController, Button
import threading
import time
import random
import math

class InputController:
    def __init__(self):
        self.keyboard = Controller()
        self.mouse = MouseController()
        self.pressed_keys = set()
        self.lock = threading.Lock()
        self.keys = {
            "f2" : ALL_KELLS.f2,
            "backspace" : ALL_KELLS.backspace,
        }

        self.response_time_range = (0.3, 0.4)
        self.release_time_range = (0.2, 0.3)
    
    def pressKey(self, key):
        with self.lock:
            if key in self.pressed_keys:
                return
            self.pressed_keys.add(key)
        
        thread = threading.Thread(target=self._execute_key_press, args=(key,))
        thread.daemon = True
        thread.start()
    
    def mouseClick(self, pos, speed_pps=1200, button=Button.left):
        """
        Inicia o processo de mover e clicar com o mouse em uma thread separada.
        :param pos: Uma tupla (x, y) com as coordenadas de destino.
        :param speed_pps: A velocidade do movimento em pixels por segundo.
        :param button: O botão do mouse a ser clicado.
        """
        thread = threading.Thread(target=self._execute_mouse_click, args=(pos, speed_pps, button))
        thread.daemon = True
        thread.start()

    def _ease_out_cubic(self, t):
        """
        Função de suavização cúbica (Ease-Out).
        Recebe um progresso linear t (0 a 1) e retorna um progresso que
        começa rápido e desacelera.
        """
        return 1 - pow(1 - t, 3)

    def _execute_key_press(self, key):
        try:
            response_delay = random.uniform(self.response_time_range[0], self.response_time_range[1])
            release_delay = random.uniform(self.release_time_range[0], self.release_time_range[1])
            current_key = key

            if current_key in self.keys:
                current_key = self.keys[current_key]

            print(f"Tempo de resposta da tecla: {response_delay:.2f}s / Tempo de pressão: {release_delay:.2f}s")

            time.sleep(response_delay)
            self.keyboard.press(current_key)
            time.sleep(release_delay)
            self.keyboard.release(current_key)
            
        finally:
            with self.lock:
                self.pressed_keys.discard(key)

    def _execute_mouse_click(self, pos, speed_pps, button):
        try:
            start_pos = self.mouse.position
            end_pos = (pos[0], pos[1] + 30)
          
            distance = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])

            if distance > 1:
                duration = distance / speed_pps
              
                p0 = start_pos
                p3 = end_pos
              
                offset_magnitude = min(distance / 2, 150)
                p1 = (
                    p0[0] + (p3[0] - p0[0]) * 0.33 + random.uniform(-offset_magnitude, offset_magnitude),
                    p0[1] + (p3[1] - p0[1]) * 0.33 + random.uniform(-offset_magnitude, offset_magnitude)
                )
                p2 = (
                    p0[0] + (p3[0] - p0[0]) * 0.66 + random.uniform(-offset_magnitude, offset_magnitude),
                    p0[1] + (p3[1] - p0[1]) * 0.66 + random.uniform(-offset_magnitude, offset_magnitude)
                )

                num_steps = int(duration * 100)
                num_steps = max(num_steps, 20)
                time_per_step = duration / num_steps

                print(f"Movendo mouse de {start_pos} para {end_pos} em {duration:.2f}s (com desaceleração)...")

                for i in range(num_steps + 1):
                    linear_t = i / num_steps
                    eased_t = self._ease_out_cubic(linear_t)
                  
                    x = (1-eased_t)**3 * p0[0] + 3*(1-eased_t)**2 * eased_t * p1[0] + 3*(1-eased_t) * eased_t**2 * p2[0] + eased_t**3 * p3[0]
                    y = (1-eased_t)**3 * p0[1] + 3*(1-eased_t)**2 * eased_t * p1[1] + 3*(1-eased_t) * eased_t**2 * p2[1] + eased_t**3 * p3[1]
                  
                    # --- ALTERAÇÃO AQUI ---
                    # Usando round() para arredondar para o pixel mais próximo, em vez de truncar com int()
                    self.mouse.position = (round(x), round(y))
                    time.sleep(time_per_step)

            self.mouse.position = end_pos
          
            response_delay = random.uniform(self.response_time_range[0], self.response_time_range[1])
            click_duration = random.uniform(self.release_time_range[0], self.release_time_range[1])
          
            time.sleep(response_delay)
            self.mouse.press(button)
            time.sleep(click_duration)
            self.mouse.release(button)
            print(f"Clique em {pos} executado.")

        except Exception as e:
            print(f"Ocorreu um erro durante o clique do mouse: {e}")

    def get_pressed_keys(self):
        with self.lock:
            return self.pressed_keys.copy()
    
    def is_key_pressed(self, key):
        with self.lock:
            return key in self.pressed_keys

# --- Exemplo de Uso ---
if __name__ == '__main__':
    controller = InputController()
    
    print("Demonstração do movimento e clique do mouse em 3 segundos...")
    print("O mouse se moverá para a posição (800, 500) e clicará.")
    
    time.sleep(3)
    
    # Chama a função com uma velocidade de 1200 pixels por segundo para ver o efeito mais claramente
    controller.mouseClick((800, 500), speed_pps=2000)
    
    print("\nA função mouseClick foi chamada. O programa principal continua.")
    print("Observe como o movimento começa rápido e desacelera perto do destino.")
    
    time.sleep(5)
    
    print("\nFim da demonstração.")