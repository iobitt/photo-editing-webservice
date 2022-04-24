from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.controllers import image_processing_controller

app = FastAPI()

app.mount("/downloadable_files", StaticFiles(directory='tmp/downloadable_files'), name="downloadable_files")

app.include_router(image_processing_controller.router)
