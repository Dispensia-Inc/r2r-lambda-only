from ..main.assembly.factory import CustomR2RProviderFactory
from .assembly.builder import CustomR2RBuilder
from core.main.assembly import R2RConfig
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional
from contextlib import asynccontextmanager
import warnings
import os
import logging
logger = logging.getLogger()

logger.info("---starte program---")


# Global scheduler
scheduler = AsyncIOScheduler()

logger.info("---completed load modules---")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("---called lifespan method---")
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
    builder = CustomR2RBuilder(config=config)
    # R2RProviderFactoryの上書き
    builder.with_provider_factory(CustomR2RProviderFactory)
    return await builder.build()


logging.basicConfig(level=logging.INFO)

config_name = os.getenv("R2R_CONFIG_NAME", os.getenv("CONFIG_NAME", None))
config_path = os.getenv("R2R_CONFIG_PATH", os.getenv("CONFIG_PATH", None))

# Check if the user is setting deprecated environment variables of CONFIG_NAME and CONFIG_PATH
if os.getenv("CONFIG_NAME"):
    warnings.warn(
        "Environment variable CONFIG_NAME is deprecated and support for it will be removed in release 3.5.0. Please use R2R_CONFIG_NAME instead."
    )
if os.getenv("CONFIG_PATH"):
    warnings.warn(
        "Environment variable CONFIG_PATH is deprecated and support for it will be removed in release 3.5.0. Please use R2R_CONFIG_PATH instead."
    )

if not config_path and not config_name:
    config_name = "default"
host = os.getenv("R2R_HOST", os.getenv("HOST", "0.0.0.0"))
port = int(os.getenv("R2R_PORT", (os.getenv("PORT", "7272"))))

# Check if the user is setting deprecated environment variables of HOST and PORT
if os.getenv("HOST"):
    warnings.warn(
        "Environment variable HOST is deprecated and support for it will be removed in release 3.5.0. Please use R2R_HOST instead."
    )
if os.getenv("PORT"):
    warnings.warn(
        "Environment variable PORT is deprecated and support for it will be removed in release 3.5.0. Please use R2R_PORT instead."
    )

logger.info(
    f"Environment R2R_CONFIG_NAME: {
        'None' if config_name is None else config_name}"
)
logger.info(
    f"Environment R2R_CONFIG_PATH: {
        'None' if config_path is None else config_path}"
)
logger.info(f"Environment R2R_PROJECT_NAME: {os.getenv('R2R_PROJECT_NAME')}")

logger.info(f"Environment R2R_POSTGRES_HOST: {os.getenv('R2R_POSTGRES_HOST')}")
logger.info(
    f"Environment R2R_POSTGRES_DBNAME: {os.getenv('R2R_POSTGRES_DBNAME')}"
)
logger.info(f"Environment R2R_POSTGRES_PORT: {os.getenv('R2R_POSTGRES_PORT')}")
logger.info(
    f"Environment R2R_POSTGRES_PASSWORD: {os.getenv('R2R_POSTGRES_PASSWORD')}"
)
logger.info(
    f"Environment R2R_PROJECT_NAME: {os.getenv('R2R_PR2R_PROJECT_NAME')}"
)

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

# -------------test-----------------


class CustomMangum(Mangum):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def set_environment(event):
        logger.info("[[ INFO ]] received invoke handler!")
        logger.info(event)
        identification_name = event["headers"]["x-acc-identification-name"]
        # TODO: 顧客IDのバリデーションを実装する
        os.environ["R2R_PROJECT_NAME"] = identification_name
        logger.info(f"[[ INFO ]] identification_name = {identification_name}")

    def __call__(self, event, context):
        self.set_environment(event)
        super().__call__(event, context)
# -------------test-----------------


# export port 8080
api_gateway_base_path = "/api/ingestion"
handler = CustomMangum(app=app, api_gateway_base_path=api_gateway_base_path)
