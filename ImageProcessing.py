import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        """
        Inicializa o processador de imagens
        """
        pass
    
    def template_matching(self, image, template):
        """
        Realiza template matching entre uma imagem e um template
        
        Args:
            image (numpy.ndarray): Imagem principal (array numpy)
            template (numpy.ndarray): Template (array numpy)
            
        Returns:
            tuple: (melhor_posicao, porcentagem_similaridade)
                - melhor_posicao: tupla (x, y) da posição do melhor match
                - porcentagem_similaridade: float de 0 a 100 representando a similaridade
        """
        try:
            if image is None or template is None:
                raise ValueError("Imagem ou template são None")
            
            # Converte para escala de cinza se necessário
            if len(image.shape) == 3:
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                image_gray = image
                
            if len(template.shape) == 3:
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            else:
                template_gray = template
            
            # Realiza o template matching usando TM_CCOEFF_NORMED
            result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # Encontra a localização do melhor match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Para TM_CCOEFF_NORMED, o melhor match é o max_loc
            melhor_posicao = max_loc
            
            # Converte o valor de similaridade para porcentagem (0-100)
            porcentagem_similaridade = max_val * 100
            
            return melhor_posicao, porcentagem_similaridade
            
        except Exception as e:
            print(f"Erro durante o template matching: {str(e)}")
            return None, 0.0
    
    def crop_image(self, image, x, y, width, height):
        """
        Corta uma região específica da imagem usando numpy
        
        Args:
            image (numpy.ndarray): Imagem a ser cortada
            x (int): Coordenada x do canto superior esquerdo
            y (int): Coordenada y do canto superior esquerdo
            width (int): Largura da região a ser cortada
            height (int): Altura da região a ser cortada
            
        Returns:
            numpy.ndarray: Imagem cortada ou None se houver erro
        """
        try:
            if image is None:
                raise ValueError("Imagem é None")
            
            # Obtém as dimensões da imagem
            img_height, img_width = image.shape[:2]
            
            # Valida as coordenadas
            if x < 0 or y < 0:
                raise ValueError("Coordenadas x e y devem ser positivas")
            if x + width > img_width or y + height > img_height:
                raise ValueError("Região de corte excede os limites da imagem")
            
            # Corta a imagem usando slicing do numpy
            cropped_image = image[y:y+height, x:x+width]
            
            return cropped_image
            
        except Exception as e:
            print(f"Erro ao cortar a imagem: {str(e)}")
            return None
    
    def crop_from_center(self, image, width, height):
        """
        Corta uma região do centro da imagem
        
        Args:
            image (numpy.ndarray): Imagem a ser cortada
            width (int): Largura da região a ser cortada
            height (int): Altura da região a ser cortada
            
        Returns:
            numpy.ndarray: Imagem cortada ou None se houver erro
        """
        try:
            if image is None:
                raise ValueError("Imagem é None")
            
            # Obtém as dimensões da imagem
            img_height, img_width = image.shape[:2]
            
            # Calcula as coordenadas do centro
            center_x = img_width // 2
            center_y = img_height // 2
            
            # Calcula as coordenadas de início do corte
            start_x = max(0, center_x - width // 2)
            start_y = max(0, center_y - height // 2)
            
            # Ajusta as dimensões se necessário
            end_x = min(img_width, start_x + width)
            end_y = min(img_height, start_y + height)
            
            # Corta a imagem
            cropped_image = image[start_y:end_y, start_x:end_x]
            
            return cropped_image
            
        except Exception as e:
            print(f"Erro ao cortar do centro: {str(e)}")
            return None
    
    def crop_template_match_area(self, image, template, padding=0):
        """
        Corta a área onde o template foi encontrado com padding opcional
        
        Args:
            image (numpy.ndarray): Imagem principal
            template (numpy.ndarray): Template
            padding (int): Pixels extras ao redor da área encontrada
            
        Returns:
            tuple: (imagem_cortada, posicao, similaridade) ou (None, None, 0.0) se não encontrar
        """
        try:
            # Encontra o template na imagem
            posicao, similaridade = self.template_matching(image, template)
            
            if posicao is None:
                print("Template não encontrado na imagem")
                return None, None, 0.0
            
            # Obtém as dimensões do template
            template_height, template_width = template.shape[:2]
            
            # Calcula as coordenadas com padding
            x = max(0, posicao[0] - padding)
            y = max(0, posicao[1] - padding)
            width = template_width + (2 * padding)
            height = template_height + (2 * padding)
            
            # Corta a área
            cropped_image = self.crop_image(image, x, y, width, height)
            
            return cropped_image, posicao, similaridade
            
        except Exception as e:
            print(f"Erro ao cortar área do template: {str(e)}")
            return None, None, 0.0
    
    def crop_multiple_regions(self, image, regions):
        """
        Corta múltiplas regiões da mesma imagem
        
        Args:
            image (numpy.ndarray): Imagem a ser cortada
            regions (list): Lista de tuplas (x, y, width, height, nome_opcional)
            
        Returns:
            list: Lista de tuplas (nome_regiao, imagem_cortada)
        """
        try:
            cropped_images = []
            
            for i, region in enumerate(regions):
                if len(region) == 4:
                    x, y, width, height = region
                    region_name = f"region_{i}"
                elif len(region) == 5:
                    x, y, width, height, region_name = region
                else:
                    print(f"Região {i} tem formato inválido. Use (x, y, width, height) ou (x, y, width, height, nome)")
                    continue
                
                # Corta a região
                cropped = self.crop_image(image, x, y, width, height)
                
                if cropped is not None:
                    cropped_images.append((region_name, cropped))
            
            return cropped_images
            
        except Exception as e:
            print(f"Erro ao cortar múltiplas regiões: {str(e)}")
            return []
    
    def template_matching_with_threshold(self, image, template, threshold=0.8):
        """
        Realiza template matching com um threshold mínimo de similaridade
        
        Args:
            image (numpy.ndarray): Imagem principal
            template (numpy.ndarray): Template
            threshold (float): Threshold mínimo (0.0 a 1.0)
            
        Returns:
            tuple: (melhor_posicao, porcentagem_similaridade) ou (None, 0.0) se não atender o threshold
        """
        posicao, similaridade = self.template_matching(image, template)
        
        if similaridade >= threshold * 100:
            return posicao, similaridade
        else:
            return None, similaridade
    
    def visualizar_resultado(self, image, template, draw_on_copy=True):
        """
        Visualiza o resultado do template matching desenhando um retângulo
        
        Args:
            image (numpy.ndarray): Imagem principal
            template (numpy.ndarray): Template
            draw_on_copy (bool): Se True, desenha em uma cópia da imagem
            
        Returns:
            numpy.ndarray: Imagem com o retângulo desenhado ou None se não encontrar
        """
        try:
            posicao, similaridade = self.template_matching(image, template)
            
            if posicao is not None:
                # Trabalha com uma cópia se solicitado
                result_image = image.copy() if draw_on_copy else image
                
                # Obtém as dimensões do template
                h, w = template.shape[:2]
                
                # Desenha um retângulo ao redor da área encontrada
                top_left = posicao
                bottom_right = (top_left[0] + w, top_left[1] + h)
                
                cv2.rectangle(result_image, top_left, bottom_right, (0, 255, 0), 2)
                
                # Adiciona texto com a porcentagem
                cv2.putText(result_image, f'{similaridade:.1f}%', 
                           (top_left[0], top_left[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                return result_image
            
            return None
            
        except Exception as e:
            print(f"Erro na visualização: {str(e)}")
            return None
    
    def apply_green_mask(self, image):
        """
        Aplica uma máscara de cor verde em uma imagem.

        Args:
            image (numpy.ndarray): Imagem de entrada (em formato BGR).

        Returns:
            numpy.ndarray: Imagem com a máscara aplicada, mostrando apenas as áreas verdes.
        """
        try:
            if image is None:
                raise ValueError("Imagem é None")

            # Converte a imagem do espaço de cores BGR para HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Define os limites inferior e superior para a cor verde no espaço HSV
            # Estes valores podem precisar de ajuste dependendo da tonalidade de verde
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])

            # Cria a máscara binária: pixels dentro do intervalo ficam brancos, o resto preto
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Aplica a máscara na imagem original usando uma operação bitwise AND
            # Isso mantém os pixels da imagem original onde a máscara é branca (verde)
            masked_image = cv2.bitwise_and(image, image, mask=mask)

            return masked_image

        except Exception as e:
            print(f"Erro ao aplicar a máscara verde: {str(e)}")
            return None

# Exemplo de uso
if __name__ == "__main__":
    # Crie ou carregue suas imagens aqui
    # Para este exemplo, vamos criar imagens de teste se não existirem
    if cv2.imread("imagem.png") is None:
        print("Criando imagem.png de teste...")
        test_img = np.zeros((500, 500, 3), dtype=np.uint8)
        test_img[100:400, 100:400] = (0, 255, 0) # Quadrado verde
        cv2.rectangle(test_img, (20, 20), (80, 80), (0, 0, 255), -1) # Quadrado vermelho
        cv2.imwrite("imagem.png", test_img)

    if cv2.imread("template.png") is None:
        print("Criando template.png de teste...")
        test_template = np.zeros((50, 50, 3), dtype=np.uint8)
        test_template[:, :] = (0, 255, 0) # Template verde
        cv2.imwrite("template.png", test_template)

    processor = ImageProcessor()
    
    # Carrega as imagens
    image = cv2.imread("imagem.png")
    template = cv2.imread("template.png")

    if image is None or template is None:
        print("Erro ao carregar as imagens. Verifique se 'imagem.png' e 'template.png' existem.")
    else:
        # Exemplo de template matching
        posicao, similaridade = processor.template_matching(image, template)
        if posicao:
            print(f"Template encontrado em: {posicao}, Similaridade: {similaridade:.2f}%")
        
        # Visualizar resultado do template matching
        result_img = processor.visualizar_resultado(image, template)
        if result_img is not None:
            cv2.imshow("Resultado Template Matching", result_img)

        # --- NOVO: Exemplo de uso da máscara verde ---
        green_masked_image = processor.apply_green_mask(image)
        if green_masked_image is not None:
            # Exibe a imagem original e a imagem com a máscara
            cv2.imshow("Imagem Original", image)
            cv2.imshow("Imagem com Mascara Verde", green_masked_image)
        
        # Aguarda uma tecla ser pressionada para fechar as janelas
        print("\nPressione qualquer tecla para fechar as janelas de imagem.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()