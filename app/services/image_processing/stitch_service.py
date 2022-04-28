import cv2

from app.services.image_processing.base_service import BaseService


class StitchService(BaseService):

    MODES = (cv2.Stitcher_PANORAMA, cv2.Stitcher_SCANS)

    def __init__(self, image_paths, output_image_path, mode=0):
        self.image_paths = image_paths
        self.output_image_path = output_image_path
        self.errors = []

        self.stitcher = cv2.Stitcher.create(self.MODES[mode])
        self.stitcher.setPanoConfidenceThresh(0.0)

    def execute(self):
        images = self.load_images()
        if self.errors:
            return [False, None, self.errors]

        result_image = self.stitch(images)
        if self.errors:
            return [False, None, self.errors]

        self.save_image(result_image)
        return [True, self.output_image_path, None]

    def load_images(self):
        images = []
        for image_path in self.image_paths:
            image = cv2.imread(image_path)
            if image is None:
                self.errors.append(f"Не смог прочитать изображение: {image_path}")
            images.append(image)
        return images

    def stitch(self, images):
        status, result_image = self.stitcher.stitch(tuple(images))
        if status != 0:
            self.errors.append(f"Не удалось склеить изображения")
        return result_image
