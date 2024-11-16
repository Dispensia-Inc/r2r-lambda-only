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

            user = {attr["Name"]: attr["Value"]
                    for attr in response["UserAttributes"]}
            user["name"] = response["Username"]

            return UserResponse(
                id=user["sub"],
                email=user["email"],
                is_active=user["custom:is_active"],
                is_superuser=user["custom:is_superuser"],
                created_at=None,
                updated_at=None,
                is_verified=True,
                name=user["name"],
            )

        except Exception as e:
            raise R2RException(status_code=401, message=str(e))
