import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

from core.main.assembly import R2RBuilder, R2RConfig
from src.main import CustomR2RProviderFactory

logger = logging.getLogger(__name__)

# Global scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    r2r_app = await create_r2r_app(
        config_name=config_name,
        config_path=config_path,
    )

    # Copy all routes from r2r_app to app
    app.router.routes = r2r_app.app.routes

    # Copy middleware and exception handlers
    app.middleware = r2r_app.app.middleware  # type: ignore
    app.exception_handlers = r2r_app.app.exception_handlers

    # Start the scheduler
    scheduler.start()

    # Start the Hatchet worker
    await r2r_app.orchestration_provider.start_worker()

    yield

    # # Shutdown
    scheduler.shutdown()


async def create_r2r_app(
    config_name: Optional[str] = "default",
    config_path: Optional[str] = None,
):
    config = R2RConfig.load(config_name, config_path)

    if (
        config.embedding.provider == "openai"
        and "OPENAI_API_KEY" not in os.environ
    ):
        raise ValueError(
            "Must set OPENAI_API_KEY in order to initialize OpenAIEmbeddingProvider."
        )

    # Build the R2RApp
    builder = R2RBuilder(config=config)
    # CustomR2RProviderFactoryを指定
    builder.with_provider_factory(CustomR2RProviderFactory)
    return await builder.build()


logging.basicConfig(level=logging.INFO)

config_name = os.getenv("R2R_CONFIG_NAME", os.getenv("CONFIG_NAME", None))
config_path = os.getenv("R2R_CONFIG_PATH", os.getenv("CONFIG_PATH", None))

if not config_path and not config_name:
    config_name = "default"

host = os.getenv("R2R_HOST", os.getenv("HOST", "0.0.0.0"))
port = int(os.getenv("R2R_PORT", (os.getenv("PORT", "7272"))))

# Create the FastAPI app
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# export port 8080
api_gateway_base_path = "/api"
handler = Mangum(app, api_gateway_base_path=api_gateway_base_path)