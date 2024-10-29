from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from core.main import IngestionRouter

from .config import R2RConfig


class CustomR2RApp:
    def __init__(
        self,
        config: R2RConfig,
        ingestion_router: IngestionRouter,
    ):
        self.config = config
        self.ingestion_router = ingestion_router
        self.app = FastAPI()
        self._setup_routes()
        self._apply_cors()

    def _setup_routes(self):
        # Include routers in the app
        self.app.include_router(self.ingestion_router, prefix="/v2")

    def _apply_cors(self):
        origins = ["*", "http://localhost:3000", "http://localhost:7272"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    async def serve(self, host: str = "0.0.0.0", port: int = 7272):
        # Start the Hatchet worker in a separate thread
        import uvicorn

        # Run the FastAPI app
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()
