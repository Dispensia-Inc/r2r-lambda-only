import os
from typing import Optional
from asyncio import get_event_loop
from fastapi import UploadFile
from pydantic import Json
from uuid import UUID

from core.main.assembly import R2RConfig

from .assembly.builder import CustomR2RBuilder
from ..main.assembly.factory import CustomR2RProviderFactory


async def create_r2r_app(config_name, config_path):
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


async def async_handler(event, context):
    config_name = os.getenv("R2R_CONFIG_NAME", os.getenv("CONFIG_NAME", None))
    config_path = os.getenv("R2R_CONFIG_PATH", os.getenv("CONFIG_PATH", None))
    os.environ["R2R_PROJECT_NAME"] = event.r2r_project_name

    await create_r2r_app(config_name, config_path)


def lambda_handler(event, context):
    return get_event_loop().run_until_complete(async_handler(event, context))
