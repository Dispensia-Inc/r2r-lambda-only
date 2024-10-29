import logging
from typing import Optional

from core.base import (
    CryptoProvider,
    DatabaseConfig,
    VectorQuantizationType,
)
from core.providers.database.postgres import PostgresDBProvider
from .base import CustomSemaphoreConnectionPool

logger = logging.getLogger()


class CustomPostgresDBProvider(PostgresDBProvider):
    def __init__(
        self,
        config: DatabaseConfig,
        dimension: int,
        crypto_provider: CryptoProvider,
        quantization_type: Optional[
            VectorQuantizationType
        ] = VectorQuantizationType.FP32,
        *args,
        **kwargs,
        ):
        super().__init__(
            config, 
            dimension, 
            crypto_provider, 
            quantization_type, 
            *args, 
            **kwargs
            )

    async def initialize(self):
        logger.info("Initializing `PostgresDBProvider`.")
        self.pool = CustomSemaphoreConnectionPool(
            self.connection_string, self.postgres_configuration_settings
        )
        await self.pool.initialize()
        await self.connection_manager.initialize(self.pool)

        async with self.pool.get_connection() as conn:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")

            # Create schema if it doesn't exist
            await conn.execute(
                f'CREATE SCHEMA IF NOT EXISTS "{self.project_name}";'
            )

        await self.document_handler.create_table()
        await self.collection_handler.create_table()
        await self.token_handler.create_table()
        await self.user_handler.create_table()
        await self.vector_handler.create_table()