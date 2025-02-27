import sys
import os
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.constants import EnvConfig
from app.routers.api import router as api_router
from app.routers.health import router as health_router


logger = logging.getLogger(__name__)
logger.warning("This is a warning from FastAPI App")

app = FastAPI(
    title="pipeline-api",
    version="1.0",
    redoc_url=None,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router)

if __name__ == "__main__":
    try:
        logger.info("Hello from FastAPI!")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.environ[EnvConfig.PORT.value]),
            log_config=None,
            reload=False
        )
    except KeyboardInterrupt:
        logger.info("Shutting Down: Process interrupeted")
    except Exception as _:
        logger.exception("Shutting Down: Exception in main process")
        sys.exit(0)
