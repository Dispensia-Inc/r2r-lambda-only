import os
import logging
import warnings
import json
from asyncio import get_event_loop
from typing import Optional

from core.main.assembly import R2RConfig
from shared.abstractions import R2RException

from lambda_functions.common.core.main.exception import LambdaException
from .assembly.builder import CustomR2RBuilder
from ..main.assembly.factory import CustomR2RProviderFactory
from .orchestration.lambda_orchestration import LambdaOrchestration

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

config_name = os.getenv("R2R_CONFIG_NAME", os.getenv("CONFIG_NAME", None))
config_path = os.getenv("R2R_CONFIG_PATH", os.getenv("CONFIG_PATH", None))

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


async def create_r2r_app(
    config_name: Optional[str] = "default",
    config_path: Optional[str] = None,
) -> LambdaOrchestration:
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


def get_token(event) -> str:
    try:
        return event["headers"]["authorization"].replace(
            "Bearer ", "")
    except Exception as e:
        logger.error(f"{e}")
        return ""


def get_body(body: str, keys: list[str]) -> dict:
    try:
        body = json.loads(body)
        res = {}
        for key in keys:
            res[key] = body[key] if key in body.keys() else None
        return res
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse request body: {e}")
        raise LambdaException(
            message="Invalid request body",
            status_code=400,
            detail={"error": str(e)}
        )


async def async_handler(event, context):
    path_prefix = "/management"
    request_path = event["path"].replace(path_prefix, "")
    request_method = event["httpMethod"]
    logger.info(f"request path: {request_path}")
    logger.info(f"request method: {request_method}")
    # TODO: 会社IDをバリデーションしてfalseならここでreturnする
    # os.environ["R2R_PROJECT_NAME"] = get_body(
    #     event["body"], ["x-acc-identification-name"])

    try:
        response_data = {}

        # R2Rを初期化
        r2r_app = await create_r2r_app(
            config_name=config_name,
            config_path=config_path,
        )
        logger.info("completed build.")

        # Controller
        match (request_path, request_method):
            case ("/create_collection", "POST"):
                token = get_token(event)
                body = get_body(
                    event["body"], ["name", "description"]
                )
                response_data = await r2r_app.create_collection(token, **body)

            case ("/update_collection", "POST"):
                token = get_token(event)
                # TODO: パスパラメータを取得してid変数に入れる
                body = get_body(
                    event["body"], ["collection_id", "name", "description"]
                )
                response_data = await r2r_app.update_collection(token, **body)

            case ("/get_collection/{collection_id}", "GET"):
                token = get_token(event)
                collection_id = event["pathParameters"]["collection_id"]
                response_data = await r2r_app.get_collection(token, collection_id)

            case ("/delete_collection/{collection_id}", "DELETE"):
                token = get_token(event)
                collection_id = event["pathParameters"]["collection_id"]
                response_data = await r2r_app.delete_collection(token, collection_id)

            case ("/add_user_to_collection", "POST"):
                token = get_token(event)
                body = get_body(
                    event["body"], ["user_id", "collection_id"]
                )
                response_data = await r2r_app.add_user_to_collection(token, **body)

            case ("/remove_user_from_collection", "POST"):
                token = get_token(event)
                body = get_body(
                    event["body"], ["user_id", "collection_id"]
                )
                response_data = await r2r_app.remove_user_from_collection(token, **body)

            case ("/user_collections/{user_id}", "GET"):
                token = get_token(event)
                user_id = event["pathParameters"]["user_id"]
                body = get_body(
                    event["body"], ["offset", "limit"]
                )
                response_data = await r2r_app.user_collections(token, user_id, **body)

            case _:
                error_response = R2RException(
                    message=f"path {event['path']} was not found.",
                    status_code=400,
                    detail={"path": event["path"]}
                )
                response_data = error_response.to_dict()

        logger.info(f"response data: {response_data}")
        return response_data

    except Exception as e:
        logger.error(f"Error in async_handler: {str(e)}", exc_info=True)
        error = R2RException(
            message="Internal server error",
            status_code=500,
            detail={"error": str(e)}
        )
        return error.to_dict()


def handler(event, context):
    logger.info(f"received event: {event}")
    try:
        return get_event_loop().run_until_complete(async_handler(event, context))
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        error = R2RException(
            message="Internal server error",
            status_code=500,
            detail={"error": str(e)}
        )
        return error.to_dict()
