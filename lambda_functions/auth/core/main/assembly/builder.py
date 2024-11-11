import logging
from typing import Any, Dict

from core.base import (
    AsyncPipe,
    EmbeddingProvider,
    FileProvider,
    IngestionProvider,
    KGProvider,
    CompletionProvider,
    PromptProvider,
    OrchestrationProvider,
    R2RLoggingProvider,
    RunManager,
)
from core.main import (
    R2RBuilder,
    R2RConfig,
    AuthService,
    R2RPipeFactory,
    R2RPipelineFactory,
)

from .factory import CustomR2RProviderFactory
from ..orchestration.lambda_orchestration import LambdaOrchestration

logger = logging.getLogger()


class CustomR2RBuilder(R2RBuilder):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    def _create_services(
        self, service_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        services = {}
        services["auth"] = AuthService(**service_params)
        return services

    async def build(
        self,
        *args,
        **kwargs
    ) -> LambdaOrchestration:
        provider_factory = self.provider_factory_override or CustomR2RProviderFactory
        pipe_factory = self.pipe_factory_override or R2RPipeFactory
        pipeline_factory = self.pipeline_factory_override or R2RPipelineFactory

        kwargs = {
            # 除外するプロバイダのオーバーライドに空のインスタンスを渡して未処理にさせる
            # (auth_provider_override, crypto_provider, database_providerは残す)
            "embedding_provider_override": EmbeddingProvider(self.config.embedding),
            "file_provider_override": FileProvider(self.config.file),
            "ingestion_provider_override": IngestionProvider(self.config.ingestion),
            "kg_provider_override": KGProvider(self.config.kg),
            "llm_provider_override": CompletionProvider(self.config.completion),
            "prompt_provider_override": PromptProvider(self.config.prompt),
            "orchestration_provider_override": OrchestrationProvider(self.config.orchestration),
            # 除外するパイプのオーバーライドに空のインスタンスを渡して未処理にさせる
            "kg_triples_extraction_pipe_override": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_storage_pipe_override": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "vector_search_pipe_override": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_search_pipe_override": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "rag_pipe_override": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "streaming_rag_pipe_override": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_entity_description_pipe": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_clustering_pipe": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_entity_deduplication_pipe": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_entity_deduplication_summary_pipe": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_community_summary_pipe": AsyncPipe(config=AsyncPipe.PipeConfig()),
            "kg_prompt_tuning_pipe": AsyncPipe(config=AsyncPipe.PipeConfig()),
            **kwargs
        }

        try:
            providers = await self._create_providers(
                provider_factory, *args, **kwargs
            )
            pipes = self._create_pipes(
                pipe_factory, providers, *args, **kwargs
            )
            pipelines = self._create_pipelines(
                pipeline_factory, pipes, *args, **kwargs
            )

        except Exception as e:
            logger.error(f"Error creating providers, pipes, or pipelines: {e}")
            raise

        run_singleton = R2RLoggingProvider()
        run_manager = RunManager(run_singleton)

        service_params = {
            "config": self.config,
            "providers": providers,
            "pipes": pipes,
            "pipelines": pipelines,
            "agents": None,
            "run_manager": run_manager,
            "logging_connection": None,
        }

        services = self._create_services(service_params)

        return LambdaOrchestration(services["auth"])
