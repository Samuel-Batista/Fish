from ImageProcessing import ImageProcessor
from Input import InputController
from wc import WindowCapture
import cv2 as cv
import time
import winsound
import random


class Bot:
    def __init__(self):
        self.status = ["idle", "fishing"]
        self.current_status = "idle"
        self.controller = InputController()
        self.imageProcessor = ImageProcessor()
        self.gameScreen = WindowCapture()

        self.last_fish_detection = time.time()
        self.fish_detection_delay_range = (10, 15)
        self.fish_detection_delay = random.uniform(self.fish_detection_delay_range[0], self.fish_detection_delay_range[1])

        self.response_time_range = (0.3, 0.45)
        self.release_time_range = (0.3, 0.35)

        self.numbers_templates = {
            "1" : cv.imread("./templates/Notifications/Numbers/1.png"),
            "2" : cv.imread("./templates/Notifications/Numbers/2.png"),
            "3" : cv.imread("./templates/Notifications/Numbers/3.png"),
            "4" : cv.imread("./templates/Notifications/Numbers/4.png"),
            "5" : cv.imread("./templates/Notifications/Numbers/5.png"),
            "6" : cv.imread("./templates/Notifications/Numbers/6.png"),
            "7" : cv.imread("./templates/Notifications/Numbers/7.png"),
            "8" : cv.imread("./templates/Notifications/Numbers/8.png"),
        }

        self.backspace_template = cv.imread("./templates/Notifications/BACKSPACE.png")


    def beep(self, frequency):
        duration = 100  # Duração do beep (ms)
        winsound.Beep(frequency, duration)
    
    def is_fishing(self):
        print("detecting if is fishing")
        success = 0
        attempts = 100

        game_img = self.gameScreen.get_screenshot()

        while attempts > 0:
            attempts -= 1
            _, accuracy = self.imageProcessor.template_matching(game_img, self.backspace_template)
            if accuracy > 90:
                success += 1

        if success > attempts * 0.8:
            return True

        return False

    def start_burning(self):
        pass