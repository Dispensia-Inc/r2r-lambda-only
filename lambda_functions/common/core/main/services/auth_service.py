from core.base import R2RException, RunManager, UserResponse
from core.main.services.base import Service
from core.main.config import R2RConfig
from core.main.abstractions import R2RAgents, R2RPipelines, R2RPipes
from core.providers.logger.r2r_logger import SqlitePersistentLoggingProvider
from core.telemetry.telemetry_decorator import telemetry_event

from ..abstractions import CustomR2RProviders


class CognitoAuthService(Service):
    def __init__(
        self,
        config: R2RConfig,
        providers: CustomR2RProviders,
        pipes: R2RPipes,
        pipelines: R2RPipelines,
        agents: R2RAgents,
        run_manager: RunManager,
        logging_connection: SqlitePersistentLoggingProvider,
    ):
        super().__init__(
            config,
            providers,
            pipes,
            pipelines,
            agents,
            run_manager,
            logging_connection,
        )

    @telemetry_event("GetCurrentUser")
    async def user(self, token: str) -> UserResponse:
        try:
            user = await self.providers.auth.user(token)
            return user
        except Exception as e:
            raise e
