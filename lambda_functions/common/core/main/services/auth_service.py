from core.base import R2RLoggingProvider, R2RException, RunManager, UserResponse
from core.main.services.base import Service
from core.main.config import R2RConfig
from core.main.abstractions import R2RAgents, R2RPipelines, R2RPipes
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
        logging_connection: R2RLoggingProvider,
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
        # TODO: CognitoAuthProviderのuserを呼び出してレスポンスを返す
        user = await self.providers.auth.user(token)
        return user
