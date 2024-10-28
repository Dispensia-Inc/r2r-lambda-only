import logging
from typing import Optional, Type

from core.main.config import R2RConfig
from core.base import (
    R2RLoggingProvider,
    RunManager,
)
from core.main.assembly import (
    R2RAgentFactory,
    R2RPipeFactory,
    R2RPipelineFactory,
    R2RProviderFactory,
)
from core.main.api.ingestion_router import IngestionRouter
from lambda_functions.ingestion.core.main.app import CustomR2RApp

logger = logging.getLogger()


class R2RBuilder:
    def __init__(self, config: R2RConfig):
        self.config = config
        self.provider_factory_override: Optional[Type[R2RProviderFactory]] = (
            None
        )
        self.pipe_factory_override: Optional[Type[R2RPipeFactory]] = None
        self.pipeline_factory_override: Optional[Type[R2RPipelineFactory]] = (
            None
        )
        self.provider_overrides = ProviderOverrides()
        self.pipe_overrides = PipeOverrides()
        self.pipeline_overrides = PipelineOverrides()
        self.service_overrides = ServiceOverrides()
        self.assistant_factory_override: Optional[R2RAgentFactory] = None
        self.rag_agent_override: Optional[R2RRAGAgent] = None

    async def build(self, *args, **kwargs) -> CustomR2RApp:
        provider_factory = self.provider_factory_override or R2RProviderFactory
        pipe_factory = self.pipe_factory_override or R2RPipeFactory
        pipeline_factory = self.pipeline_factory_override or R2RPipelineFactory

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

        assistant_factory = self.assistant_factory_override or R2RAgentFactory(
            self.config, providers, pipelines
        )
        agents = assistant_factory.create_agents(
            overrides={"rag_agent": self.rag_agent_override}, *args, **kwargs
        )

        run_singleton = R2RLoggingProvider()
        run_manager = RunManager(run_singleton)

        service_params = {
            "config": self.config,
            "providers": providers,
            "pipes": pipes,
            "pipelines": pipelines,
            "agents": agents,
            "run_manager": run_manager,
            "logging_connection": run_singleton,
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
            orchestration_provider=orchestration_provider,
            **routers,
        )