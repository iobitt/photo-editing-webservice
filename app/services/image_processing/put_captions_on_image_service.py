import cv2
import numpy as np

from app.services.image_processing.base_service import BaseService


LABELS = open("lib/darknet/data/coco.names").read().strip().split("\n")
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
FONT_SCALE = 1
THICKNESS = 1


class PutCaptionsOnImageService(BaseService):

    def __init__(self, image, detection_result):
        super().__init__(image)
        self.detection_result = detection_result

    def execute(self):
        return self.put_captions()

    def put_captions(self):
        image = self.image

        for detection in self.detection_result:
            # рисуем прямоугольник ограничивающей рамки и подписываем на изображении
            color = [int(c) for c in COLORS[detection['class_id']]]
            cv2.rectangle(image,
                          (detection['x'], detection['y']),
                          (detection['x'] + detection['w'], detection['y'] + detection['h']),
                          color=color, thickness=THICKNESS)
            text = f"{LABELS[detection['class_id']]}: {detection['confidence']:.2f}"
            # вычисляем ширину и высоту текста, чтобы рисовать прозрачные поля в качестве фона текста
            (text_width, text_height) = \
                cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=FONT_SCALE, thickness=THICKNESS)[0]
            text_offset_x = detection['x']
            text_offset_y = detection['y'] - 5
            box_coords = ((text_offset_x, text_offset_y), (text_offset_x + text_width + 2, text_offset_y - text_height))
            overlay = image.copy()
            cv2.rectangle(overlay, box_coords[0], box_coords[1], color=color, thickness=cv2.FILLED)
            # добавить непрозрачность (прозрачность поля)
            image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
            # теперь поместите текст (метка: доверие%)
            cv2.putText(image, text, (detection['x'], detection['y'] - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=FONT_SCALE, color=(0, 0, 0), thickness=THICKNESS)
        return image
