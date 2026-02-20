from fastapi import FastAPI
from app.api.routes import router
from app.api.error_handlers import generic_exception_handler



app = FastAPI(
    title="ConvoDNA - Multimodal Conversation Intelligence API",
    version="1.0.0",
    description="Backend API for analyzing multimodal customer conversations"
)

app.add_exception_handler(Exception, generic_exception_handler)
app.include_router(router)
