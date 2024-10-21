from core.providers.database.postgres import PostgresDBProvider
from src.providers.database.relational import CustomPostgresRelationalDBProvider
from typing import Optional
from core.base import (
    CryptoProvider,
    DatabaseConfig,
    RelationalDBProvider,
)
from shared.abstractions.vector import VectorQuantizationType

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
            config=config,
            dimension=dimension,
            crypto_provider=crypto_provider,
            quantization_type=quantization_type,
            *args,
            **kwargs,
        )

    async def _initialize_relational_db(self) -> RelationalDBProvider:
        relational_db = CustomPostgresRelationalDBProvider(
            self.config,
            connection_string=self.connection_string,
            crypto_provider=self.crypto_provider,
            project_name=self.project_name,
            postgres_configuration_settings=self.postgres_configuration_settings,
        )
        await relational_db.initialize()
        return relational_db