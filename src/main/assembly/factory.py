from typing import Optional, Any
from core.base import (
    DatabaseConfig,
    CryptoProvider,
    DatabaseProvider,
    FileConfig,
    FileProvider,
    PromptConfig,
    PromptProvider,
)
from core.main import R2RProviderFactory
from core.main.config import R2RConfig


class CustomR2RProviderFactory(R2RProviderFactory):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    async def create_database_provider(
        self,
        db_config: DatabaseConfig,
        crypto_provider: CryptoProvider,
        *args,
        **kwargs,
    ) -> DatabaseProvider:
        database_provider: Optional[DatabaseProvider] = None
        if not self.config.embedding.base_dimension:
            raise ValueError(
                "Embedding config must have a base dimension to initialize database."
            )

        vector_db_dimension = self.config.embedding.base_dimension
        quantization_type = (
            self.config.embedding.quantization_settings.quantization_type
        )
        if db_config.provider == "postgres":
            from src.providers import CustomPostgresDBProvider

            database_provider = CustomPostgresDBProvider(
                db_config,
                vector_db_dimension,
                crypto_provider=crypto_provider,
                quantization_type=quantization_type,
            )
            await database_provider.initialize()
            return database_provider
        else:
            raise ValueError(
                f"Database provider {db_config.provider} not supported"
            )
