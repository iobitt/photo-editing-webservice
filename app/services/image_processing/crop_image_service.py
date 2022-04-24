from app.services.image_processing.base_service import BaseService


class CropImageService(BaseService):

    def __init__(self, image_path, output_image_path, x, y, width, height):
        super().__init__(image_path, output_image_path)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def execute(self):
        new_image = self.crop_image(self.image, self.x, self.y, self.width, self.height)
        self.save_image(new_image)

    @staticmethod
    def crop_image(image, x, y, width, height):
        return image[y:y + height, x:x + width]
