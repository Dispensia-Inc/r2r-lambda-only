from typing import Any, Optional

from core.base import (
    AsyncPipe,
    DatabaseConfig,
    CryptoProvider,
    DatabaseProvider,
    AuthProvider,
    CompletionProvider,
    EmbeddingProvider,
    FileProvider,
    IngestionProvider,
    PromptProvider,
)
from core.main.config import R2RConfig
from core.main import (
    R2RProviderFactory,
)
from core.providers import PostgresKGProvider
from core.main.abstractions import R2RProviders


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

        dimension = self.config.embedding.base_dimension
        quantization_type = (
            self.config.embedding.quantization_settings.quantization_type
        )
        if db_config.provider == "postgres":
            from lambda_functions.ingestion.core.providers.database.postgres import CustomPostgresDBProvider

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

    async def create_providers(
        self,
        auth_provider_override: Optional[AuthProvider] = None,
        crypto_provider_override: Optional[CryptoProvider] = None,
        database_provider_override: Optional[DatabaseProvider] = None,
        embedding_provider_override: Optional[EmbeddingProvider] = None,
        file_provider_override: Optional[FileProvider] = None,
        ingestion_provider_override: Optional[IngestionProvider] = None,
        llm_provider_override: Optional[CompletionProvider] = None,
        prompt_provider_override: Optional[PromptProvider] = None,
        orchestration_provider_override: Optional[Any] = None,
        *args,
        **kwargs,
    ) -> R2RProviders:
        embedding_provider = (
            embedding_provider_override
            or self.create_embedding_provider(
                self.config.embedding, *args, **kwargs
            )
        )

        ingestion_provider = (
            ingestion_provider_override
            or self.create_ingestion_provider(
                self.config.ingestion, *args, **kwargs
            )
        )

        llm_provider = llm_provider_override or self.create_llm_provider(
            self.config.completion, *args, **kwargs
        )

        crypto_provider = (
            crypto_provider_override
            or self.create_crypto_provider(self.config.crypto, *args, **kwargs)
        )

        database_provider = (
            database_provider_override
            or await self.create_database_provider(
                self.config.database, crypto_provider, *args, **kwargs
            )
        )

        prompt_provider = (
            prompt_provider_override
            or await self.create_prompt_provider(
                self.config.prompt, database_provider, *args, **kwargs
            )
        )

        # PostgresKGProviderをインスタンス化
        kg_provider = PostgresKGProvider(
            self.config.kg,
            database_provider,
            embedding_provider
        )

        auth_provider = (
            auth_provider_override
            or await self.create_auth_provider(
                self.config.auth,
                database_provider,
                crypto_provider,
                *args,
                **kwargs,
            )
        )

        file_provider = file_provider_override or await self.create_file_provider(
            self.config.file, database_provider, *args, **kwargs  # type: ignore
        )

        orchestration_provider = (
            orchestration_provider_override
            or self.create_orchestration_provider(self.config.orchestration)
        )

        return R2RProviders(
            auth=auth_provider,
            database=database_provider,
            embedding=embedding_provider,
            ingestion=ingestion_provider,
            llm=llm_provider,
            prompt=prompt_provider,
            kg=kg_provider,
            orchestration=orchestration_provider,
            file=file_provider,
        )
