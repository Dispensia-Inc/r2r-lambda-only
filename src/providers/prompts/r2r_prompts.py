import logging
import asyncpg

from core.base import DatabaseProvider, PromptConfig
from core.providers.prompts.r2r_prompts import R2RPromptProvider

logger = logging.getLogger()

class CustomR2RPromptProvider(R2RPromptProvider):
    def __init__(self, config: PromptConfig,  db_provider: DatabaseProvider):
        super().__init__(
            config=config,
            db_provider=db_provider
        )
    
    async def initialize(self):
        try:
            self.pool = await asyncpg.create_pool(
                self.db_provider.connection_string,
                min_size=1,
                max_size=self.db_provider.postgres_configuration_settings.max_connections,
                max_inactive_connection_lifetime=10
            )
            logger.info(
                "custom - R2RPromptProvider successfully connected to Postgres database."
            )
            logger.info(
                f"custom - max_size={self.db_provider.postgres_configuration_settings.max_connections}"
            )
            async with self.pool.acquire() as conn:
                await conn.execute('CREATE EXTENSION IF NOT EXISTS "lo";')

            await self.create_table()
            await self._load_prompts_from_database()
            await self._load_prompts_from_yaml_directory()
        except Exception as e:
            logger.error(f"Failed to initialize R2RPromptProvider: {e}")
            raise
