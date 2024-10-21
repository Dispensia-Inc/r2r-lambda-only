import logging
import asyncpg

from core.providers.database.relational import PostgresRelationalDBProvider

logger = logging.getLogger()

class CustomPostgresRelationalDBProvider(PostgresRelationalDBProvider):
    def __init__(
        self,
        config,
        connection_string,
        crypto_provider,
        project_name,
        postgres_configuration_settings,
    ):
        super().__init__(
            config=config,
            connection_string=connection_string,
            crypto_provider=crypto_provider,
            project_name=project_name,
            postgres_configuration_settings=postgres_configuration_settings,
        )

    async def initialize(self):
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=self.postgres_configuration_settings.max_connections,
                max_inactive_connection_lifetime=10
            )

            logger.info(
                "Successfully connected to Postgres database and created connection pool."
            )
        except Exception as e:
            raise ValueError(
                f"Error {e} occurred while attempting to connect to relational database."
            ) from e

        await self._initialize_relational_db()