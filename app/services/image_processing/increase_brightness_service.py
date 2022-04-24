import cv2

from app.services.image_processing.base_service import BaseService


class IncreaseBrightnessService(BaseService):

    def __init__(self, image_path, output_image_path, brightness_diff):
        super().__init__(image_path, output_image_path)
        self.brightness_diff = brightness_diff

    def execute(self):
        new_image = self.increase_brightness(self.image, self.brightness_diff)
        self.save_image(new_image)

    @staticmethod
    def increase_brightness(image, brightness_diff):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        lim = 255 - brightness_diff
        v[v > lim] = 255
        v[v <= lim] += brightness_diff

        final_hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
