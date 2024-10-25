import asyncio
import logging
import asyncpg

from core.providers.database.base import SemaphoreConnectionPool

logger = logging.getLogger()


class CustomSemaphoreConnectionPool(SemaphoreConnectionPool):
    def __init__(self, connection_string, postgres_configuration_settings):
        super().__init__(connection_string, postgres_configuration_settings)
    
    async def initialize(self):
        try:
            logger.info(
                f"Connecting with {int(self.postgres_configuration_settings.max_connections * 0.9)} connections to `asyncpg.create_pool`."
            )

            self.semaphore = asyncio.Semaphore(
                int(self.postgres_configuration_settings.max_connections * 0.9)
            )

            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=self.postgres_configuration_settings.max_connections,
                max_inactive_connection_lifetime=0.2
            )

            logger.info(
                "Successfully connected to Postgres database and created connection pool."
            )
        except Exception as e:
            raise ValueError(
                f"Error {e} occurred while attempting to connect to relational database."
            ) from e