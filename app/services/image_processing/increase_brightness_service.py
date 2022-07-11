import cv2

from app.services.image_processing.base_service import BaseService


class IncreaseBrightnessService(BaseService):

    def __init__(self, image, brightness_diff):
        super().__init__(image)
        self.brightness_diff = brightness_diff

    def execute(self):
        return self.increase_brightness()

    def increase_brightness(self):
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        lim = 255 - self.brightness_diff
        v[v > lim] = 255
        v[v <= lim] += self.brightness_diff

        final_hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
