import logging
from typing import Any, Dict, Type

from core.base import (
    AsyncPipe,
    RunManager,
)
from core.main import (
    R2RBuilder,
    R2RConfig,
    R2RPipeFactory,
    R2RPipelineFactory,
)
from core.main.services import RetrievalService
from core.main.services.management_service import ManagementService
from src.main.assembly.factory import CustomR2RProviderFactory

from ..orchestration.lambda_orchestration import LambdaOrchestration
from lambda_functions.common.core.main.services.auth_service import CognitoAuthService

logger = logging.getLogger()


class CustomR2RBuilder(R2RBuilder):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    async def _create_providers(
        self, provider_factory: Type[CustomR2RProviderFactory], *args, **kwargs
    ) -> Any:
        overrides = {
            k: v
            for k, v in vars(self.provider_overrides).items()
            if v is not None
        }
        kwargs = {**kwargs, **overrides}
        factory = provider_factory(self.config)
        return await factory.create_providers(*args, **kwargs)

    def _create_services(
        self, service_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        services = {}
        services["auth"] = CognitoAuthService(**service_params)
        services["management"] = ManagementService(**service_params)
        services["retrieval"] = RetrievalService(**service_params)
        return services

    async def build(
        self,
        *args,
        **kwargs
    ) -> LambdaOrchestration:
        provider_factory = self.provider_factory_override or CustomR2RProviderFactory
        pipe_factory = self.pipe_factory_override or R2RPipeFactory
        pipeline_factory = self.pipeline_factory_override or R2RPipelineFactory

        try:
            providers = await self._create_providers(
                provider_factory, *args, **kwargs
            )

            run_manager = RunManager(providers.logging)

            async_pipe = AsyncPipe(
                config=AsyncPipe.PipeConfig(),
                logging_provider=providers.logging,
                run_manager=run_manager
            )

            kwargs = {
                # 除外するパイプのオーバーライドに空のインスタンスを渡して未処理にさせる
                "kg_triples_extraction_pipe_override": async_pipe,
                "kg_storage_pipe_override": async_pipe,
                "vector_storage_pipe_override": async_pipe,
                "streaming_rag_pipe_override": async_pipe,
                "kg_entity_description_pipe": async_pipe,
                "kg_clustering_pipe": async_pipe,
                "kg_entity_deduplication_pipe": async_pipe,
                "kg_entity_deduplication_summary_pipe": async_pipe,
                "kg_community_summary_pipe": async_pipe,
                "kg_prompt_tuning_pipe": async_pipe,
                **kwargs
            }

            pipes = self._create_pipes(
                pipe_factory, providers, *args, **kwargs
            )
            pipelines = self._create_pipelines(
                pipeline_factory, providers, pipes, *args, **kwargs
            )

        except Exception as e:
            logger.error(f"Error creating providers, pipes, or pipelines: {e}")
            raise

        service_params = {
            "config": self.config,
            "providers": providers,
            "pipes": pipes,
            "pipelines": pipelines,
            "agents": None,
            "run_manager": run_manager,
            "logging_connection": providers.logging,
        }

        services = self._create_services(service_params)

        return LambdaOrchestration(**services)
