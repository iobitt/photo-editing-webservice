import cv2
import requests

from app.services.image_processing.base_service import BaseService
from app.secrets import IBM_SSD_MODEL_URL


CONFIDENCE = 0.5


# https://hub.docker.com/r/codait/max-object-detector
# https://github.com/IBM/MAX-Object-Detector-Web-App
class IbmSsd(BaseService):

    def __init__(self, image, min_confidence=CONFIDENCE):
        super().__init__(image)
        self.min_confidence = min_confidence

    def execute(self):
        return self.detect()

    def detect(self):
        success, encoded_image = cv2.imencode('.png', self.image)
        files = {'image': encoded_image.tobytes()}
        values = {'threshold': self.min_confidence}
        response = requests.post(IBM_SSD_MODEL_URL, files=files, data=values)
        return self.result_mapper(response.json())

    def result_mapper(self, result):
        height, width, channels = self.image.shape
        mapped_predictions = []
        for prediction in result['predictions']:
            y1 = int(prediction['detection_box'][0] * height)
            x1 = int(prediction['detection_box'][1] * width)
            y2 = int(prediction['detection_box'][2] * height)
            x2 = int(prediction['detection_box'][3] * width)
            mapped_result = {
                'y': y1,
                'x': x1,
                'h': y2 - y1,
                'w': x2 - x1,
                'class_id': int(prediction['label_id']),
                'label': prediction['label'],
                'confidence': float(prediction['probability'])
            }
            mapped_predictions.append(mapped_result)
        return mapped_predictions
