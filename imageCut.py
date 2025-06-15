import os
from PIL import Image
import glob

def resize_images_to_fullhd(input_folder, output_folder=None):
    """
    Redimensiona todas as imagens de uma pasta para Full HD (1920x1080)
    Corta começando da esquerda e do topo
    
    Args:
        input_folder: Pasta com as imagens originais
        output_folder: Pasta de destino (opcional, se não especificada usa a mesma pasta)
    """
    
    # Se não especificar pasta de saída, usa a mesma pasta de entrada
    if output_folder is None:
        output_folder = input_folder
    
    # Cria pasta de saída se não existir
    os.makedirs(output_folder, exist_ok=True)
    
    # Extensões de imagem suportadas
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
    
    # Resolução Full HD
    target_size = (1920, 1080)
    
    processed_count = 0
    
    # Processa cada extensão
    for extension in extensions:
        # Encontra todas as imagens com a extensão atual
        pattern = os.path.join(input_folder, extension)
        image_files = glob.glob(pattern, recursive=False)
        
        # Adiciona versões maiúsculas
        pattern_upper = os.path.join(input_folder, extension.upper())
        image_files.extend(glob.glob(pattern_upper, recursive=False))
        
        for image_path in image_files:
            try:
                # Abre a imagem
                with Image.open(image_path) as img:
                    # Converte para RGB se necessário (para salvar como JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Redimensiona e corta começando da esquerda/topo
                    img_resized = resize_and_crop_from_left(img, target_size)
                    
                    # Define nome do arquivo de saída
                    filename = os.path.basename(image_path)
                    name, ext = os.path.splitext(filename)
                    
                    # Se for a mesma pasta, adiciona sufixo
                    if input_folder == output_folder:
                        output_path = os.path.join(output_folder, f"{name}_fullhd{ext}")
                    else:
                        output_path = os.path.join(output_folder, filename)
                    
                    # Salva a imagem redimensionada
                    img_resized.save(output_path, quality=95, optimize=True)
                    processed_count += 1
                    print(f"✓ Processada: {filename}")
                    
            except Exception as e:
                print(f"✗ Erro ao processar {image_path}: {str(e)}")
    
    print(f"\n🎉 Processamento concluído! {processed_count} imagens redimensionadas para Full HD.")

def resize_and_crop_from_left(img, target_size):
    """
    Redimensiona e corta a imagem para o tamanho alvo
    Corta começando da esquerda (horizontal) e do topo (vertical)
    """
    target_width, target_height = target_size
    img_width, img_height = img.size
    
    # Calcula as proporções
    img_ratio = img_width / img_height
    target_ratio = target_width / target_height
    
    if img_ratio > target_ratio:
        # Imagem mais larga - ajusta pela altura
        new_height = target_height
        new_width = int(target_height * img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Corta começando da ESQUERDA (left = 0)
        img_cropped = img_resized.crop((0, 0, target_width, target_height))
    else:
        # Imagem mais alta - ajusta pela largura
        new_width = target_width
        new_height = int(target_width / img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Corta começando do TOPO (top = 0)
        img_cropped = img_resized.crop((0, 0, target_width, target_height))
    
    return img_cropped

# Exemplo de uso
if __name__ == "__main__":
    # Especifique o caminho da pasta com as imagens
    pasta_imagens = input("Digite o caminho da pasta com as imagens: ").strip()
    
    # Verifica se a pasta existe
    if not os.path.exists(pasta_imagens):
        print("❌ Pasta não encontrada!")
    else:
        # Pergunta se quer salvar em pasta separada
        opcao = input("Salvar em pasta separada? (s/n): ").strip().lower()
        
        if opcao == 's':
            pasta_saida = input("Digite o caminho da pasta de saída: ").strip()
            resize_images_to_fullhd(pasta_imagens, pasta_saida)
        else:
            resize_images_to_fullhd(pasta_imagens)