from fastapi import FastAPI
from fastapi_server.database import engine, Base
from fastapi_server.routers import auth, events, businesses, admin
from fastapi.staticfiles import StaticFiles
from fastapi_server.routers import payments

import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(businesses.router)
app.include_router(admin.router)
app.include_router(payments.router)


# Mount static files for uploads
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.get("/")
def root():
    return {"message": "Vervigo Server is running!"}
6