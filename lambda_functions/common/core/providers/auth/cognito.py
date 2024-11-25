import os
import json
import boto3
import datetime

from core.base import (
    AuthConfig,
    AuthProvider,
    CryptoProvider,
    DatabaseProvider,
    EmailProvider,
    R2RException
)
from core.base.api.models import UserResponse


class CognitoAuthProvider(AuthProvider):
    def __init__(
            self,
            config: AuthConfig,
            crypto_provider: CryptoProvider,
            database_provider: DatabaseProvider,
            email_provider: EmailProvider
    ):
        super().__init__(config, crypto_provider, database_provider, email_provider)
        self.client = boto3.client(
            'cognito-idp',
            # 注意：以下はLambdaの環境変数で設定しない（本番環境ではデフォルトで設定されているため）
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_REGION"]
        )

    async def user(self, token: str) -> UserResponse:
        try:
            response = self.client.get_user(AccessToken=token)

            user_data = {attr["Name"]: attr["Value"]
                         for attr in response["UserAttributes"]}
            user_data["name"] = response["Username"]

            # テレメトリ送信時にユーザーIDも送りたいため必要
            os.environ["COGNITO_USER_ID"] = user_data["sub"]

            return UserResponse(
                id=user_data["sub"],
                email=user_data["email"],
                is_active=user_data["custom:is_active"],
                is_superuser=user_data["custom:is_superuser"],
                collection_ids=json.loads(user_data["custom:collection_ids"]),
                name=user_data["name"],
                bio=user_data["custom:bio"],
                profile_picture=user_data["custom:profile_picture"],
                is_verified=user_data["email_verified"],
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )

        except Exception as e:
            raise R2RException(status_code=401, message=str(e))

    # 以下はcognitoで行うため空のまま実装する
    def create_access_token(self, **kwargs):
        pass

    def create_refresh_token(self, **kwargs):
        pass

    def decode_token(self, **kwargs):
        pass

    def get_current_active_user(self, **kwargs):
        pass

    def register(self, **kwargs):
        pass

    def verify_email(self, **kwargs):
        pass

    def login(self, **kwargs):
        pass

    def refresh_access_token(self, **kwargs):
        pass

    def change_password(self, **kwargs):
        pass

    def request_password_reset(self, **kwargs):
        pass

    def confirm_password_reset(self, **kwargs):
        pass

    def logout(self, **kwargs):
        pass

    async def send_reset_email(self, email: str) -> dict[str, str]:
        pass
