from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, users, image_processing

app = FastAPI()

app.mount("/downloadable_files", StaticFiles(directory='tmp/downloadable_files'), name="downloadable_files")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(image_processing.router)
