from time import sleep
from Input import InputController
import winsound
from ImageProcessing import ImageProcessor
import cv2 as cv

controller = InputController()

processor = ImageProcessor()

def emit_beep():
    """Emite um beep sonoro"""
    frequency = 350  # Frequência do beep (Hz)
    duration = 100  # Duração do beep (ms)
    winsound.Beep(frequency, duration)


import os
import glob
from time import sleep

pasta = "./testes"

templates = {
    "1" : cv.imread("./templates/1.png"),
    "2" : cv.imread("./templates/2.png"),
    "3" : cv.imread("./templates/3.png"),
    "4" : cv.imread("./templates/4.png"),
    "5" : cv.imread("./templates/5.png"),
    "6" : cv.imread("./templates/6.png"),
    "7" : cv.imread("./templates/7.png"),
    "8" : cv.imread("./templates/8.png"),
}


for arquivo_png in glob.glob(os.path.join(pasta, "*.png")):
    
    full_img = cv.imread(arquivo_png)
    img = processor.crop_image(cv.imread(arquivo_png), 30, 680, 270, 400)

    processed_img = processor.apply_green_mask(img)

    cv.imshow("preview", img)
    cv.imshow("processed", processed_img)
    
    bestAcuracy = None
    bestIndex = None

    for index, template in templates.items():
        processed_template = processor.apply_green_mask(template)
        pos, acuracy = processor.template_matching(processed_img, processed_template)

        if not bestIndex:
            bestIndex = index
            bestAcuracy = acuracy
            continue

        if bestAcuracy and bestAcuracy < acuracy:
            bestAcuracy = acuracy
            bestIndex = index

    print(bestIndex + " : " + str(bestAcuracy))

    cv.waitKey(3000)