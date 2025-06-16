from ImageProcessing import ImageProcessor
from Input import InputController
from wc import WindowCapture
import cv2 as cv
import time
import winsound
import random

keyborad = InputController()
screen = WindowCapture()
imgProcessor = ImageProcessor()

templates = {
    "1" : cv.imread("./templates/Notifications/Numbers/1.png"),
    "2" : cv.imread("./templates/Notifications/Numbers/2.png"),
    "3" : cv.imread("./templates/Notifications/Numbers/3.png"),
    "4" : cv.imread("./templates/Notifications/Numbers/4.png"),
    "5" : cv.imread("./templates/Notifications/Numbers/5.png"),
    "6" : cv.imread("./templates/Notifications/Numbers/6.png"),
    "7" : cv.imread("./templates/Notifications/Numbers/7.png"),
    "8" : cv.imread("./templates/Notifications/Numbers/8.png"),
}

def emit_beep():
    """Emite um beep sonoro"""
    frequency = 350  # Frequência do beep (Hz)
    duration = 100  # Duração do beep (ms)
    winsound.Beep(frequency, duration)


# import os
# import glob
# from time import sleep

# pasta = "./testes"

# for arquivo_png in glob.glob(os.path.join(pasta, "*.png")):
    
#     img = imgProcessor.crop_image(cv.imread(arquivo_png), 30, 680, 270, 400)

#     cv.imshow("preview", img)
    
#     bestAcuracy = None
#     bestIndex = None

#     for index, template in templates.items():
#         pos, acuracy = imgProcessor.template_matching(img, template)

#         if not bestIndex:
#             bestIndex = index
#             bestAcuracy = acuracy
#             continue

#         if bestAcuracy and bestAcuracy < acuracy:
#             bestAcuracy = acuracy
#             bestIndex = index

#     cv.waitKey(1000)


lastDetection = time.time()
current_delay = 0

while True:

    img = imgProcessor.crop_image(screen.get_screenshot(), 30, 680, 270, 360)
    processed_img = imgProcessor.apply_green_mask(img)

    bestAcuracy = None
    bestIndex = None

    for index, template in templates.items():
        processed_template = imgProcessor.apply_green_mask(template)
        pos, acuracy = imgProcessor.template_matching(processed_img, processed_template)

        if not bestIndex:
            bestIndex = index
            bestAcuracy = acuracy
            continue

        if bestAcuracy and bestAcuracy < acuracy:
            bestAcuracy = acuracy
            bestIndex = index
    
    if bestAcuracy > 90:
        if time.time() - lastDetection > current_delay:
            current_delay = random.uniform(10, 15)
            lastDetection = time.time()
            
            # response
            print(bestIndex, bestAcuracy)
            emit_beep()

            keyborad.pressNum(bestIndex, random.uniform(0.3, 0.4), random.uniform(0.2, 0.3))

    
    cv.imshow("preview", img)
    cv.waitKey(1)