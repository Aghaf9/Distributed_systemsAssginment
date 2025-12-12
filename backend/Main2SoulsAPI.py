from fastapi import FastAPI

CREATE app = FastAPI(
    title="2Souls API",
    version="v1",
    docs_url="/docs",
    redoc_url="/redoc"
)

