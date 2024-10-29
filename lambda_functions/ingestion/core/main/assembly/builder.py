import logging

from core.base import (
    R2RLoggingProvider,
    RunManager,
)
from core.main import (
    R2RApp,
    R2RBuilder,
    R2RConfig,
    IngestionRouter,
)
from .factory import CustomR2RProviderFactory, CustomR2RPipeFactory


logger = logging.getLogger()


class CustomR2RBuilder(R2RBuilder):
    def __init__(self, config: R2RConfig):
        super().__init__(config)

    async def build(self, *args, **kwargs) -> R2RApp:
        provider_factory = self.provider_factory_override or CustomR2RProviderFactory
        pipe_factory = self.pipe_factory_override or CustomR2RPipeFactory

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
            "auth_router": None,
            "ingestion_router": IngestionRouter(
                services["ingestion"],
                orchestration_provider=orchestration_provider,
            ).get_router(),
            "management_router": None,
            "retrieval_router": None,
            "kg_router": None,
        }

        return R2RApp(
            config=self.config,
            orchestration_provider=orchestration_provider,
            **routers,
        )
