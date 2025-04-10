from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from v1.v1_routes import version_v1

app = FastAPI()
app.include_router(version_v1)
# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific origins in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
