import os
import re
import logging
import warnings
from asyncio import get_event_loop
from typing import Optional

from core.main.assembly import R2RConfig

from .assembly.builder import CustomR2RBuilder
from ..main.assembly.factory import CustomR2RProviderFactory

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
    # TODO: CustomR2RProviderFactoryでオーバーライドするのやめたい
    builder.with_provider_factory(CustomR2RProviderFactory)
    return await builder.build()


config = R2RConfig.load(config_name, config_path)

version_prefix = "v2"


def get_token(event) -> str:
    try:
        return event["queryStringParameters"]["Authorization"].relpace(
            "Bearer ", "")
    except:
        return ""


async def async_handler(event):
    r2r_app = await create_r2r_app(
        config_name=config_name,
        config_path=config_path,
    )

    # TODO: event pathから取得されるpath_prefixの形式を確認して修正
    request_path = event["pathParameters"]["proxy"].replace(version_prefix, "")
    request_method = event["httpMethod"]

    # TODO: それぞれの関数に引数を渡す
    # Controller
    match (request_path, request_method):
        case ("/register", "POST"):
            return r2r_app.register(email, password)
        case ("/login", "POST"):
            return r2r_app.login(form_data)
        case ("/verify_email", "POST"):
            return r2r_app.verify_email(email, verification_code)
        case ("/logout", "POST"):
            token = get_token(event)
            return r2r_app.logout(token)
        case ("/user", "GET"):
            token = get_token(event)
            return r2r_app.get_user(token)
        case ("/user", "PUT"):
            return r2r_app.update_user()
        case ("/user", "DELETE"):
            return r2r_app.delete_user()
        case ("/refresh_access_token", "POST"):
            return r2r_app.refresh_access_token()
        case ("/change_password", "POST"):
            return r2r_app.change_password()
        case ("/request_password_reset", "POST"):
            return r2r_app.request_password_reset()
        case ("/reset_password", "POST"):
            return r2r_app.reset_password()
        case _:
            uuid_reg_pattern = "([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})"
            user_id_match = re.match(f"/user/{uuid_reg_pattern}", request_path)
            user_id = user_id_match.group() if user_id_match else ""
            if (user_id and request_method == "DELETE"):
                token = get_token(event)
                # TODO: auth tokenとパスワードを引数に指定する
                return r2r_app.delete_user(user_id, password)
            else:
                return {"msg": f"path {event['path']} is 404 not found."}


def handler(event, context):
    logger.info(f"received event: {event}")
    return get_event_loop().run_until_complete(async_handler(event, context))
