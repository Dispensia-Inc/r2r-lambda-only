from typing import Optional

from core.base import (
    AuthConfig,
    DatabaseConfig,
    CryptoProvider,
    DatabaseProvider,
    AuthProvider,
)
from core.main.config import R2RConfig
from core.main import (
    R2RProviderFactory,
)


class AWSR2RProviderFactory(R2RProviderFactory):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    async def create_auth_provider(
        auth_config: AuthConfig,
        db_provider: DatabaseProvider,
        crypto_provider: CryptoProvider,
        *args,
        **kwargs,
    ) -> AuthProvider:
        if auth_config.provider == "r2r":
            from core.providers import R2RAuthProvider

            r2r_auth = R2RAuthProvider(
                auth_config, crypto_provider, db_provider
            )
            await r2r_auth.initialize()
            return r2r_auth
        elif auth_config.provider == "supabase":
            from core.providers import SupabaseAuthProvider

            return SupabaseAuthProvider(
                auth_config, crypto_provider, db_provider
            )
        elif auth_config.provider == "cognito":
            from lambda_functions.common.core.providers.auth.cognito import CognitoAuthProvider

            return CognitoAuthProvider(
                auth_config, crypto_provider, db_provider
            )
        else:
            raise ValueError(
                f"Auth provider {auth_config.provider} not supported."
            )

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

        dimension = self.config.embedding.base_dimension
        quantization_type = (
            self.config.embedding.quantization_settings.quantization_type
        )
        if db_config.provider == "postgres":
            from lambda_functions.common.core.providers.database.postgres import CustomPostgresDBProvider

            database_provider = CustomPostgresDBProvider(
                db_config,
                dimension,
                crypto_provider=crypto_provider,
                quantization_type=quantization_type,
            )
            await database_provider.initialize()
            return database_provider
        else:
            raise ValueError(
                f"Database provider {db_config.provider} not supported"
            )
