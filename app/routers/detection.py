from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

PREFIX = '/detection'

router = APIRouter(
    tags=['detection'],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/detect", description='Найти объекты на изображении')
async def detect(image: UploadFile, background_tasks: BackgroundTasks):
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

