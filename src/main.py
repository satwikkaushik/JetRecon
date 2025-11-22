from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from utils.config import config
from utils.errors import custom_validation_error_handler
from middlewares.error_handler import ErrorHandlerMiddleware
from routers.jobs import router as jobs_router

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register custom exception handlers
app.add_exception_handler(RequestValidationError, custom_validation_error_handler)
app.add_middleware(ErrorHandlerMiddleware)

# Register routers
app.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])


# Basic health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=config.DEFAULT_HOST, port=int(config.DEFAULT_PORT))
