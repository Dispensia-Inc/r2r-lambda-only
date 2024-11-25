import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from functools import wraps

from core.telemetry.posthog import telemetry_client
from core.telemetry.events import ErrorEvent, FeatureUsageEvent
from core.telemetry.telemetry_decorator import (
    ProductTelemetryClient
)

logger = logging.getLogger()

# テレメトリのユーザーIDをCognitoのユーザーIDにする


class CustomProductTelemetryClient(ProductTelemetryClient):
    @property
    def user_id(self) -> str:
        return os.environ["COGNITO_USER_ID"]


product_telemetry_client = CustomProductTelemetryClient()


def get_project_metadata():
    import platform

    return {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "version": product_telemetry_client.version,
    }


# Create a thread pool with a fixed number of workers
telemetry_thread_pool: Optional[ThreadPoolExecutor] = None

if os.getenv("TELEMETRY_ENABLED", "true").lower() in ("true", "1"):
    telemetry_thread_pool = ThreadPoolExecutor(max_workers=2)


def telemetry_event(event_name):
    def decorator(func):
        def log_telemetry(event_type, user_id, metadata, error_message=None):

            if telemetry_thread_pool is None:
                return

            try:
                if event_type == "feature":
                    telemetry_client.capture(
                        FeatureUsageEvent(
                            user_id=user_id,
                            properties=metadata,
                            feature=event_name,
                        )
                    )
                elif event_type == "error":
                    telemetry_client.capture(
                        ErrorEvent(
                            user_id=user_id,
                            properties=metadata,
                            endpoint=event_name,
                            error_message=error_message,
                        )
                    )
            except Exception as e:
                logger.error(f"Error in telemetry event logging: {str(e)}")

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if telemetry_thread_pool is None:
                return await func(*args, **kwargs)

            metadata = get_project_metadata()
            user_id = product_telemetry_client.user_id

            try:
                result = await func(*args, **kwargs)
                telemetry_thread_pool.submit(
                    log_telemetry, "feature", user_id, metadata
                )
                return result
            except Exception as e:
                telemetry_thread_pool.submit(
                    log_telemetry, "error", user_id, metadata, str(e)
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    async_wrapper(*args, **kwargs), loop
                )
                return future.result()
            else:
                return loop.run_until_complete(async_wrapper(*args, **kwargs))

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator
