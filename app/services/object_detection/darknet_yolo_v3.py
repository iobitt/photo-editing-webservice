import time
import cv2
import numpy as np
import os.path

from app.services.image_processing.base_service import BaseService


CONFIG_PATH = 'lib/darknet/cfg/yolov3.cfg'
WEIGHTS_PATH = 'lib/darknet/yolov3.weights'
LABELS = open("lib/darknet/data/coco.names").read().strip().split("\n")
BLOB_SIZE = (416, 416)
CONFIDENCE = 0.5
SCORE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5
FONT_SCALE = 1
THICKNESS = 1


# https://pjreddie.com/darknet/yolo/
# https://waksoft.susu.ru/2021/05/19/kak-vypolnit-obnaruzhenie-obektov-yolo-s-pomoshhyu-opencv-i-pytorch-v-python/
class DarknetYoloV3(BaseService):

    def __init__(self, image, min_confidence=CONFIDENCE):
        super().__init__(image)
        self.min_confidence = min_confidence

    def execute(self):
        return self.detect()

    def detect(self):
        if not os.path.exists(WEIGHTS_PATH):
            raise Exception('Отсутствует файл yolov3.weights')

        net = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)

        layer_names = net.getLayerNames()
        layer_names = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        image_height, image_weight = self.image.shape[:2]

        blob = cv2.dnn.blobFromImage(self.image, 1 / 255.0, BLOB_SIZE, swapRB=True, crop=False)
        net.setInput(blob)
        start = time.perf_counter()
        layer_outputs = net.forward(layer_names)
        time_took = time.perf_counter() - start
        print("Time took:", time_took)

        boxes, confidences, class_ids = self.process_result(layer_outputs, image_height, image_weight,
                                                            self.min_confidence)

        # выполнить не максимальное подавление с учетом оценок, определенных ранее
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, SCORE_THRESHOLD, IOU_THRESHOLD)

        return self.get_output(boxes, confidences, class_ids, idxs)

    @staticmethod
    def process_result(layer_outputs, image_height, image_weight, min_confidence):
        boxes, confidences, class_ids = [], [], []
        # loop over each of the layer outputs
        for output in layer_outputs:
            # перебираем все обнаруженные объекты
            for detection in output:
                # извлекаем идентификатор класса (метку) и достоверность (как вероятность)
                # обнаружение текущего объекта
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                # отбросим слабые прогнозы, убедившись, что у обнаруженных
                # вероятность больше минимальной вероятности
                if confidence > min_confidence:
                    # масштабируем координаты ограничивающего прямоугольника относительно
                    # размер изображения, учитывая, что YOLO на самом деле
                    # возвращает центральные координаты (x, y) ограничивающего
                    # поля, за которым следуют ширина и высота полей
                    box = detection[:4] * np.array([image_weight, image_height, image_weight, image_height])
                    (centerX, centerY, width, height) = box.astype("int")

                    # используем центральные координаты (x, y) для получения вершины и
                    # и левый угол ограничительной рамки
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # обновить наш список координат ограничивающего прямоугольника, достоверности,
                    # и идентификаторы класса
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        return boxes, confidences, class_ids

    @staticmethod
    def get_output(boxes, confidences, class_ids, idxs):
        if not len(idxs):
            return []

        output = []
        for i in idxs.flatten():
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            output.append({
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'class_id': int(class_ids[i]),
                'label': LABELS[class_ids[i]],
                'confidence': confidences[i]
            })
        return output
