from fastapi import APIRouter, UploadFile, BackgroundTasks, Request
from typing import List
import uuid
import aiofiles
import os

from app.services.image_processing.increase_brightness_service import IncreaseBrightnessService
from app.services.image_processing.crop_image_service import CropImageService
from app.services.image_processing.stitch_service import StitchService

from app.app_redis import *

router = APIRouter()

UPLOADED_FILES_DIR = 'tmp/uploaded_files/'
DOWNLOADED_FILES_DIR = 'tmp/downloadable_files/'


@router.get("/image_processing/get_status", description="Получить статус операции", tags=["image"])
async def get_status(job_id: str, request: Request):
    job = redis.hgetall(job_id)
    if not job:
        return {'ok': False, 'error': 'Операция с таким ID не найдена'}

    result = {'ok': True, 'job': job}
    if job['status'] == 'Завершено успешно':
        downloadable_url = request.url_for('downloadable_files', path=f"/{job['id']}.png")
        result['downloadable_url'] = downloadable_url

    return result

# TODO: исправить под Redis
# @router.post("/image_processing/increase_brightness", description="Увеличить яркость изображения", tags=["image"])
# async def increase_brightness(value: int, file: UploadFile, background_tasks: BackgroundTasks):
#     if value <= 0:
#         return {'ok': False, 'error': 'value должен быть больше 0'}
#
#     file_path = await save_input_file(file)
#     background_tasks.add_task(increase_brightness_task, file_path, value)
#     return {'ok': True, 'new_file_name': file_path}
#
#
# @router.post("/image_processing/crop_image", description="Обрезать изображение", tags=["image"])
# async def crop_image(x: int, y: int, width: int, height: int, file: UploadFile, background_tasks: BackgroundTasks):
#     file_path = await save_input_file(file)
#     background_tasks.add_task(crop_image_task, file_path, x, y, width, height)
#     return {'ok': True, 'new_file_name': file_path}


@router.post("/image_processing/stitch_image", tags=["image"], description="Склеить изображения")
async def stitch_images(images: List[UploadFile], background_tasks: BackgroundTasks):
    job = {'id': uuid.uuid4().hex, 'status': 'Создан'}
    redis.hmset(job['id'], job)

    folder_path = f"{UPLOADED_FILES_DIR}{job['id']}"
    os.mkdir(folder_path)

    images_path = []
    for file in images:
        file_path = await save_input_file(file, folder_path)
        images_path.append(file_path)

    background_tasks.add_task(stitch_images_task, f"{job['id']}.png", job['id'], images_path)

    job['status'] = 'Добавлен в очередь'
    redis.hmset(job['id'], job)

    return {'ok': True, 'job_id': job['id'], 'job_status': job['status']}


async def save_input_file(file, folder_path):
    file_body = await file.read()
    full_path = f"{folder_path}/{file.filename}"

    async with aiofiles.open(full_path, 'wb') as out_file:
        await out_file.write(file_body)

    return full_path


def increase_brightness_task(file_name: str, brightness_diff):
    image_path = f"{UPLOADED_FILES_DIR}{file_name}"
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    IncreaseBrightnessService(image_path, output_image_path, brightness_diff).execute()


def crop_image_task(file_name: str, x, y, width, height):
    image_path = f"{UPLOADED_FILES_DIR}{file_name}"
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    CropImageService(image_path, output_image_path, x, y, width, height).execute()


def stitch_images_task(file_name: str, job_id, image_paths):
    job = redis.hgetall(job_id)
    job['status'] = 'Выполняется'
    redis.hmset(job['id'], job)

    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    status, result, errors = StitchService(image_paths, output_image_path).execute()

    if status:
        job['status'] = 'Завершено успешно'
    else:
        job['status'] = 'Завершено c ошибкой'
        job['error'] = ', '.join(errors)
    redis.hmset(job['id'], job)
