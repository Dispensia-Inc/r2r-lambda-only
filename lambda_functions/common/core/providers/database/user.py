from core.base.providers.crypto import CryptoProvider
from core.providers.database.base import PostgresConnectionManager
from core.providers.database.user import PostgresUserHandler


# ユーザーテーブルを拡張する
class CustomPostgresUserHandler(PostgresUserHandler):
    def __init__(
            self,
            project_name: str,
            connection_manager: PostgresConnectionManager,
            crypto_provider: CryptoProvider):
        super().__init__(
            project_name,
            connection_manager,
            crypto_provider)

    async def create_tables(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self._get_table_name(PostgresUserHandler.TABLE_NAME)} (
            user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            openid_sub TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_superuser BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            verification_code TEXT,
            verification_code_expiry TIMESTAMPTZ,
            name TEXT,
            bio TEXT,
            profile_picture TEXT,
            identification_name TEXT NOT NULL,
            slack_user_id TEXT,
            chatwork_user_id TEXT,
            teams_team_id TEXT,
            reset_token TEXT,
            reset_token_expiry TIMESTAMPTZ,
            collection_ids UUID[] NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),


        );
        """
        await self.connection_manager.execute_query(query)
