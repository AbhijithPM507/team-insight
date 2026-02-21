from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router
from app.api.error_handlers import generic_exception_handler
from app.core.logging_config import setup_logging


# -------------------------
# Setup Logging
# -------------------------
setup_logging()
logger = logging.getLogger("main")

logger.info("Starting ConvoDNA API...")


# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(
    title="ConvoDNA - Multimodal Conversation Intelligence API",
    version="1.0.0",
    description="Backend API for analyzing multimodal customer conversations"
)


# -------------------------
# CORS Middleware (for UI)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon mode (allow all)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Exception Handler
# -------------------------
app.add_exception_handler(Exception, generic_exception_handler)


# -------------------------
# Routes
# -------------------------
app.include_router(router)


logger.info("ConvoDNA API started successfully.")