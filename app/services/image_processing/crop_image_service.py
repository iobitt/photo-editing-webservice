from app.services.image_processing.base_service import BaseService


class CropImageService(BaseService):

    def __init__(self, image, x, y, width, height):
        super().__init__(image)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def execute(self):
        return self.crop_image()

    def crop_image(self):
        return self.image[self.y:self.y + self.height, self.x:self.x + self.width]
