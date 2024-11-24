from typing import Any, Optional, Union
import logging

from core.base import (
    IngestionProvider,
)
from core.providers import (
    R2RAuthProvider,
    SupabaseAuthProvider,
    BCryptProvider,
    PostgresDBProvider,
    AsyncSMTPEmailProvider,
    ConsoleMockEmailProvider,
    LiteLLMEmbeddingProvider,
    OpenAIEmbeddingProvider,
    OllamaEmbeddingProvider,
    R2RIngestionProvider,
    UnstructuredIngestionProvider,
    OpenAICompletionProvider,
    LiteLLMCompletionProvider,
    SqlitePersistentLoggingProvider
)
from core.main.config import R2RConfig


from lambda_functions.common.core.main.assembly.factory import AWSR2RProviderFactory
from lambda_functions.common.core.main.abstractions import CustomR2RProviders

logger = logging.getLogger()


class CustomR2RProviderFactory(AWSR2RProviderFactory):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    async def create_providers(
        self,
        auth_provider_override: Optional[
            Union[R2RAuthProvider, SupabaseAuthProvider]
        ] = None,
        crypto_provider_override: Optional[BCryptProvider] = None,
        database_provider_override: Optional[PostgresDBProvider] = None,
        email_provider_override: Optional[
            Union[AsyncSMTPEmailProvider, ConsoleMockEmailProvider]
        ] = None,
        embedding_provider_override: Optional[
            Union[
                LiteLLMEmbeddingProvider,
                OpenAIEmbeddingProvider,
                OllamaEmbeddingProvider,
            ]
        ] = None,
        ingestion_provider_override: Optional[
            Union[R2RIngestionProvider, UnstructuredIngestionProvider]
        ] = None,
        llm_provider_override: Optional[
            Union[OpenAICompletionProvider, LiteLLMCompletionProvider]
        ] = None,
        orchestration_provider_override: Optional[Any] = None,
        r2r_logging_provider_override: Optional[
            SqlitePersistentLoggingProvider
        ] = None,
        *args,
        **kwargs,
    ) -> CustomR2RProviders:
        embedding_provider = (
            embedding_provider_override
            or self.create_embedding_provider(
                self.config.embedding, *args, **kwargs
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

        # インスタンス化のみ
        ingestion_provider = IngestionProvider(
            self.config.ingestion,
            database_provider,
            llm_provider,
        )

        email_provider = (
            email_provider_override
            or await self.create_email_provider(
                self.config.email, crypto_provider, *args, **kwargs
            )
        )

        auth_provider = (
            auth_provider_override
            or await self.create_auth_provider(
                self.config.auth,
                crypto_provider,
                database_provider,
                email_provider,
                *args,
                **kwargs,
            )
        )

        orchestration_provider = (
            orchestration_provider_override
            or self.create_orchestration_provider(self.config.orchestration)
        )

        logging_provider = (
            r2r_logging_provider_override
            or SqlitePersistentLoggingProvider(self.config.logging)
        )
        await logging_provider.initialize()

        return CustomR2RProviders(
            auth=auth_provider,
            database=database_provider,
            embedding=embedding_provider,
            ingestion=ingestion_provider,
            llm=llm_provider,
            email=email_provider,
            orchestration=orchestration_provider,
            logging=logging_provider,
        )
