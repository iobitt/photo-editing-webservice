from fastapi import APIRouter, UploadFile, BackgroundTasks, Request, Depends
from bson.objectid import ObjectId
from typing import List, Union
import aiofiles
import os
import cv2

from app.models.user import User
from app.services.image_processing.increase_brightness_service import IncreaseBrightnessService
from app.services.image_processing.crop_image_service import CropImageService
from app.services.image_processing.stitch_service import StitchService
from app.services.object_detection.darknet_yolo_v3 import DarknetYoloV3
from app.services.object_detection.ibm_ssd import IbmSsd
from app.services.image_processing.put_captions_on_image_service import PutCaptionsOnImageService
from app.dependencies import get_current_user
from app.db.db import db


UPLOADED_FILES_DIR = 'tmp/uploaded_files/'
DOWNLOADED_FILES_DIR = 'tmp/downloadable_files/'

AVAILABLE_OBJECT_DETECTION_MODEL_NAMES = {'yolo', 'ssd'}


router = APIRouter(
    prefix='/image_processing',
    tags=['image_processing']
)


@router.get("/get_job_status", description="Получить статус операции по обработке изображения")
async def get_status(job_id: str, request: Request, current_user: User = Depends(get_current_user)):
    job = db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        return {'ok': False, 'error': 'Операция с таким ID не найдена'}

    del job['_id']
    job['job_id'] = job_id
    result = {'ok': True, 'job': job}

    if job['status'] == 'done':
        downloadable_url = request.url_for('downloadable_files', path=f"/{job['job_id']}.png")
        result['downloadable_url'] = downloadable_url

    return result


@router.post("/increase_brightness", description="Увеличить яркость изображения")
async def increase_brightness(value: int, image: UploadFile, background_tasks: BackgroundTasks,
                              current_user: User = Depends(get_current_user)):
    if value <= 0:
        return {'ok': False, 'error': 'value должен быть больше 0'}

    job_id = create_job(current_user)

    folder_path = f"{UPLOADED_FILES_DIR}{job_id}"
    os.mkdir(folder_path)

    image_path = await save_input_file(image, folder_path)
    background_tasks.add_task(increase_brightness_task, f"{job_id}.png", job_id, image_path, value)
    db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'added_to_queue'}})

    return {'ok': True, 'job_id': job_id, 'job_status': 'Добавлена в очередь на выполнение'}


@router.post("/crop_image", description="Обрезать изображение")
async def crop_image(x: int, y: int, width: int, height: int, image: UploadFile,
                     background_tasks: BackgroundTasks,
                     current_user: User = Depends(get_current_user)):
    job_id = create_job(current_user)

    folder_path = f"{UPLOADED_FILES_DIR}{job_id}"
    os.mkdir(folder_path)

    image_path = await save_input_file(image, folder_path)
    background_tasks.add_task(crop_image_task, f"{job_id}.png", job_id, image_path, x, y, width, height)
    db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'added_to_queue'}})

    return {'ok': True, 'job_id': job_id, 'job_status': 'Добавлена в очередь на выполнение'}


@router.post("/stitch_image", description="Склеить изображения")
async def stitch_images(images: List[UploadFile],
                        background_tasks: BackgroundTasks,
                        current_user: User = Depends(get_current_user)):
    job_id = create_job(current_user)

    folder_path = f"{UPLOADED_FILES_DIR}{job_id}"
    os.mkdir(folder_path)

    images_path = []
    for file in images:
        file_path = await save_input_file(file, folder_path)
        images_path.append(file_path)

    background_tasks.add_task(stitch_images_task, f"{job_id}.png", job_id, images_path)
    db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'added_to_queue'}})

    return {'ok': True, 'job_id': job_id, 'job_status': 'Добавлена в очередь на выполнение'}


@router.post("/detect", description="Определить объекты на изображении")
async def detect_objects(image: UploadFile,
                         background_tasks: BackgroundTasks,
                         current_user: User = Depends(get_current_user),
                         model_name: Union[str, None] = 'yolo',
                         min_confidence: Union[float, None] = 0.5,
                         border_size: Union[int, None] = 1,
                         with_labels: Union[bool, None] = True,
                         full_output: Union[bool, None] = True):

    if model_name not in AVAILABLE_OBJECT_DETECTION_MODEL_NAMES:
        return {'ok': False, 'error': f"Параметр model_name должен принимать одно из следующих значений: "
                                      f"{AVAILABLE_OBJECT_DETECTION_MODEL_NAMES}"}

    job_id = create_job(current_user)

    folder_path = f"{UPLOADED_FILES_DIR}{job_id}"
    os.mkdir(folder_path)

    image_path = await save_input_file(image, folder_path)
    background_tasks.add_task(object_detection_task,
                              f"{job_id}.png",
                              job_id,
                              image_path,
                              model_name=model_name,
                              min_confidence=min_confidence,
                              border_width=border_size,
                              with_labels=with_labels,
                              full_output=full_output)

    db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'added_to_queue'}})

    return {'ok': True, 'job_id': job_id, 'job_status': 'Добавлена в очередь на выполнение'}


async def save_input_file(file, folder_path):
    file_body = await file.read()
    full_path = f"{folder_path}/{file.filename}"

    async with aiofiles.open(full_path, 'wb') as out_file:
        await out_file.write(file_body)

    return full_path


def job_decorator(func):
    def wrapper(*args, **kwargs):
        job_id = args[1]
        db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'in_progress'}})
        try:
            result = func(*args, **kwargs)
            db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'done', 'result': result}})
            return result
        except Exception as ex:
            db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {'status': 'error', 'error': str(ex)}})
            raise ex
    return wrapper


@job_decorator
def increase_brightness_task(file_name: str, job_id, image_path, brightness_diff):
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"

    image = cv2.imread(image_path)
    result_image = IncreaseBrightnessService(image, brightness_diff).execute()
    cv2.imwrite(output_image_path, result_image)

    return {}


@job_decorator
def crop_image_task(file_name: str, job_id, image_path, x, y, width, height):
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    image = cv2.imread(image_path)
    result_image = CropImageService(image, x, y, width, height).execute()
    cv2.imwrite(output_image_path, result_image)

    return {}


@job_decorator
def stitch_images_task(file_name: str, job_id, image_paths):
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"

    images = []
    for image_path in image_paths:
        images.append(cv2.imread(image_path))

    status, result_image, errors = StitchService(images).execute()
    cv2.imwrite(output_image_path, result_image)
    return status, errors


@job_decorator
def object_detection_task(file_name: str,
                          job_id, image_path,
                          model_name='yolo',
                          min_confidence=0.5,
                          border_width=1,
                          with_labels=True,
                          full_output=True):
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    image = cv2.imread(image_path)
    if model_name == 'yolo':
        result = DarknetYoloV3(image, min_confidence=min_confidence).execute()
    elif model_name == 'ssd':
        result = IbmSsd(image, min_confidence=min_confidence).execute()
    else:
        raise Exception('unavalible model_name')

    result_image = PutCaptionsOnImageService(image,
                                             result,
                                             border_width=border_width,
                                             with_labels=with_labels).execute()
    cv2.imwrite(output_image_path, result_image)

    if full_output:
        return result
    else:
        return {'detection_count': count_unique_objects_number(result)}


def create_job(user):
    return str(db.jobs.insert_one({'status': 'created', 'user_id': user.id}).inserted_id)


def count_unique_objects_number(detection_result):
    count = {}
    for detection_result in detection_result:
        if detection_result['label'] in count:
            count[detection_result['label']] += 1
        else:
            count[detection_result['label']] = 1
    return count
