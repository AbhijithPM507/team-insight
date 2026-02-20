from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="ConvoDNA – Context-Aware Risk & Intent Intelligence Engine",
    version="1.0.0",
    description="Enterprise-grade multimodal conversation intelligence backend."
)

app.include_router(router)