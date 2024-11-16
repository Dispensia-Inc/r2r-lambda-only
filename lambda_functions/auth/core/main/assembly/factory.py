from typing import Any, Optional
import logging

from core.base import (
    AuthConfig,
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
from core.providers import PostgresKGProvider
from core.main.abstractions import R2RProviders
from core.providers import R2RPromptProvider

from lambda_functions.common.core.main.assembly.factory import AWSR2RProviderFactory

logger = logging.getLogger()


class CustomR2RProviderFactory(AWSR2RProviderFactory):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

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

        # インスタンス化のみ
        ingestion_provider = IngestionProvider(self.config.ingestion)

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

        # インスタンス化のみ
        prompt_provider = R2RPromptProvider(
            self.config.prompt, database_provider)

        # インスタンス化のみ
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
