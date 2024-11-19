import json
import boto3

from core.base import (
    AuthConfig,
    AuthProvider,
    CryptoProvider,
    R2RException
)
from core.base.api.models import UserResponse


class CognitoAuthProvider(AuthProvider):
    def __init__(
            self,
            config: AuthConfig,
            crypto_provider: CryptoProvider):
        super().__init__(config, crypto_provider)
        self.client = boto3.client('cognito-idp')

    async def user(self, token: str) -> UserResponse:
        try:
            response = self.client.get_user(AccessToken=token)

            user_data = {attr["Name"]: attr["Value"]
                         for attr in response["UserAttributes"]}
            user_data["name"] = response["Username"]

            return UserResponse(
                id=user_data["sub"],
                email=user_data["email"],
                is_active=user_data["custom:is_active"],
                is_superuser=user_data["custom:is_superuser"],
                collection_ids=json.loads(user_data["custom:collection_ids"]),
                name=user_data["name"],
                bio=user_data["custom:bio"],
                profile_picture=user_data["custom:profile_picture"],
                is_verified=user_data["custom:is_verified"],
                created_at=None,
                updated_at=None,
            )

        except Exception as e:
            raise R2RException(status_code=401, message=str(e))
