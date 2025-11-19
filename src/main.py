from fastapi import FastAPI
from utils.config import config


app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=config.DEFAULT_HOST, port=int(config.DEFAULT_PORT))
