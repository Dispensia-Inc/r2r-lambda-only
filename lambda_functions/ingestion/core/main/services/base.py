from abc import ABC

from ..config import R2RConfig

# TODO: Serviceを書く
class Service(ABC):
    def __init__(
        self,
        config: R2RConfig,
        providers: R2RProviders,
        pipes: R2RPipes,
        run_manager: RunManager,
    ):
        self.config = config
        self.providers = providers
        self.pipes = pipes
        self.run_manager = run_manager