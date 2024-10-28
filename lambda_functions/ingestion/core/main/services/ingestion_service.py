from .base import Service

# TODO: IngestionServiceを書く
class IngestionService(Service):
    # TODO: ここのservice_paramsもいくつか必要なさそう
    def __init__(
        self,
        config: R2RConfig,
        providers: R2RProviders,
        pipes: R2RPipes,
        run_manager: RunManager,
    ) -> None:
        super().__init__(
            config,
            providers,
            pipes,
            run_manager,
        )