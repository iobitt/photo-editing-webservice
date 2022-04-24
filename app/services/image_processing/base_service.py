import cv2


class BaseService:

    def __init__(self, image_path, output_image_path):
        self.image = cv2.imread(image_path)
        self.output_image_path = output_image_path

    def execute(self):
        raise Exception("To be implemented")

    def save_image(self, image):
        cv2.imwrite(self.output_image_path, image)
