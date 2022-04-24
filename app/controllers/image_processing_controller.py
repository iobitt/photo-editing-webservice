from fastapi import APIRouter, UploadFile, BackgroundTasks
import uuid
import aiofiles
import time
from os.path import exists

from app.services.image_processing.increase_brightness_service import IncreaseBrightnessService
from app.services.image_processing.crop_image_service import CropImageService

router = APIRouter()

UPLOADED_FILES_DIR = 'tmp/uploaded_files/'
DOWNLOADED_FILES_DIR = 'tmp/downloadable_files/'


@router.get("/image_processing/get_status", description="Получить статус операции", tags=["image"])
async def get_status(file_name: str):
    file_path = f"{DOWNLOADED_FILES_DIR}/{file_name}"
    file_exists = exists(file_path)
    return {'ok': True, 'ready': file_exists, 'file_name': file_name}


@router.post("/image_processing/increase_brightness", description="Увеличить яркость изображения", tags=["image"])
async def increase_brightness(value: int, file: UploadFile, background_tasks: BackgroundTasks):
    if value <= 0:
        return {'ok': False, 'error': 'value должен быть больше 0'}

    file_path = await save_input_file(file)
    background_tasks.add_task(increase_brightness, file_path, value)
    return {'ok': True, 'new_file_name': file_path}


@router.post("/image_processing/crop_image", description="Обрезать изображение", tags=["image"])
async def crop_image(x: int, y: int, width: int, height: int, file: UploadFile, background_tasks: BackgroundTasks):
    file_path = await save_input_file(file)
    background_tasks.add_task(crop_image, file_path, x, y, width, height)
    return {'ok': True, 'new_file_name': file_path}


async def save_input_file(file):
    file_body = await file.read()
    job_id = uuid.uuid4().hex
    file_extension = file.filename.split('.')[-1]

    async with aiofiles.open(f"{UPLOADED_FILES_DIR}/{job_id}.{file_extension}", 'wb') as out_file:
        await out_file.write(file_body)

    return f"{job_id}.{file_extension}"


def increase_brightness(file_name: str, brightness_diff):
    time.sleep(30)  # Симуляция длительной операции
    image_path = f"{UPLOADED_FILES_DIR}{file_name}"
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    IncreaseBrightnessService(image_path, output_image_path, brightness_diff).execute()


def crop_image(file_name: str, x, y, width, height):
    time.sleep(30)  # Симуляция длительной операции
    image_path = f"{UPLOADED_FILES_DIR}{file_name}"
    output_image_path = f"{DOWNLOADED_FILES_DIR}{file_name}"
    CropImageService(image_path, output_image_path, x, y, width, height).execute()
