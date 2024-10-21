import logging
import asyncpg

from core.base import FileConfig
from core.providers.file.postgres import PostgresFileProvider
from core.providers.database.postgres import PostgresDBProvider

logger = logging.getLogger()

class CustomPostgresFileProvider(PostgresFileProvider):
    def __init__(
        self,
        config: FileConfig,
        db_provider: PostgresDBProvider
    ):
        super().__init__(
            config=config,
            db_provider=db_provider
        )

    async def initialize(self):
        
        self.pool = await asyncpg.create_pool(
            self.db_provider.connection_string,
            min_size=1,
            max_size=self.db_provider.postgres_configuration_settings.max_connections,
            max_inactive_connection_lifetime=10
        )
        logger.info(
            "File provider successfully connected to Postgres database."
        )

        async with self.pool.acquire() as conn:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "lo";')

        await self.create_table()