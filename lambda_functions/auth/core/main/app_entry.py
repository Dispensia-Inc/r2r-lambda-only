import os
import logging
import warnings
import json
from asyncio import get_event_loop
from typing import Optional

from core.main.assembly import R2RConfig

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
        return event["queryStringParameters"]["Authorization"].relpace(
            "Bearer ", "")
    except:
        return ""


def get_body(body: str, keys: list[str]) -> dict:
    body = json.loads(body)
    res = {}
    for key in keys:
        res[key] = body[key] if key in body.keys() else None
    return res


async def async_handler(event, context):
    r2r_app = await create_r2r_app(
        config_name=config_name,
        config_path=config_path,
    )

    path_prefix = "/auth"
    request_path = event["path"].replace(path_prefix, "")
    request_method = event["httpMethod"]
    logger.info("completed build.")
    logger.info(f"request path: {request_path}")
    logger.info(f"request method: {request_method}")

    response_data = {}

    # Controller
    match (request_path, request_method):
        case ("/register", "POST"):
            body = get_body(event["body"], ["email", "password"])
            data = await r2r_app.register(**body)
            response_data = vars(data)

        case ("/login", "POST"):
            body = get_body(event["body"], ["username", "password"])
            data = await r2r_app.login(**body)
            response_data = {
                "access_token": data["access_token"].model_dump_json(),
                "refresh_token": data["refresh_token"].model_dump_json(),
            }

        case ("/verify_email", "POST"):
            body = get_body(
                event["body"], ["email", "verification_code"])
            data = await r2r_app.verify_email(**body)
            response_data = data.model_dump_json()

        case ("/logout", "POST"):
            token = get_token(event)
            data = await r2r_app.logout(token)
            response_data = data.model_dump_json()

        case ("/user", "GET"):
            token = get_token(event)
            data = await r2r_app.get_user(token)
            response_data = vars(data)

        case ("/user", "PUT"):
            body = get_body(
                event["body"], ["user_id", "email", "is_superuser"])
            data = await r2r_app.update_user(**body)
            response_data = vars(data)

        case ("/refresh_access_token", "POST"):
            data = await r2r_app.refresh_access_token(event["body"])
            response_data = vars(data)

        case ("/change_password", "POST"):
            token = get_token(event)
            body = get_body(
                event["body"], ["current_password", "new_password"])
            data = await r2r_app.change_password(token=token, **body)
            response_data = vars(data)

        case ("/request_password_reset", "POST"):
            data = await r2r_app.request_password_reset(event["body"])
            response_data = vars(data)

        case ("/reset_password", "POST"):
            body = get_body(
                event["body"], ["reset_token", "new_password"])
            data = await r2r_app.reset_password(**body)
            response_data = vars(data)

        case _:
            if ("/user" in request_path and request_method == "DELETE"):
                user_id = request_path.replace("/user/")
                token = get_token(event)
                body = get_body(
                    event["body"], ["password", "delete_vector_data"])
                data = await r2r_app.delete_user(token=token, user_id=user_id, **body)
                response_data = vars(data)

            else:
                response_data = {"msg": f"path {
                    event['path']} is 404 not found."}

    logger.info(f"response data: {response_data}")
    return response_data


def handler(event, context):
    logger.info(f"received event: {event}")
    return get_event_loop().run_until_complete(async_handler(event, context))
