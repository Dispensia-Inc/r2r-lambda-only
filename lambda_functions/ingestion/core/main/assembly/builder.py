import logging
from typing import Any, Dict

from core.base import (
    AsyncPipe,
    R2RLoggingProvider,
    RunManager,
)
from core.main import (
    R2RBuilder,
    R2RConfig,
    IngestionService,
    R2RPipeFactory,
    IngestionRouter,
)

from .factory import CustomR2RProviderFactory
from ..app import CustomR2RApp

logger = logging.getLogger()


class CustomR2RBuilder(R2RBuilder):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    def _create_services(
        self, service_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        services = {}
        # IngestionServiceだけインスタンス化する
        services["ingestion"] = IngestionService(**service_params)
        return services

    async def build(
        self,
        *args,
        **kwargs
    ):
        provider_factory = self.provider_factory_override or CustomR2RProviderFactory
        pipe_factory = self.pipe_factory_override or R2RPipeFactory

        # 除外するパイプのオーバーライドに空のインスタンスを渡す
        kwargs = {
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
        except Exception as e:
            logger.error(f"Error creating providers, pipes, or pipelines: {e}")
            raise

        run_singleton = R2RLoggingProvider()
        run_manager = RunManager(run_singleton)

        service_params = {
            "config": self.config,
            "providers": providers,
            "pipes": pipes,
            "pipelines": None,
            "agents": None,
            "run_manager": run_manager,
            "logging_connection": None,
        }

        services = self._create_services(service_params)

        orchestration_provider = providers.orchestration

        routers = {
            "ingestion_router": IngestionRouter(
                services["ingestion"],
                orchestration_provider=orchestration_provider,
            ).get_router(),
        }

        return CustomR2RApp(
            config=self.config,
            **routers,
        )
