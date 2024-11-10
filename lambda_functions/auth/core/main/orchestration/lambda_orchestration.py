from pydantic import BaseModel, ValidationError

from core.base import R2RException
from core.main.services.auth_service import AuthService


class Register(BaseModel):
    email: str
    password: str


def handle_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return e
    return inner


class LambdaOrchestration:
    def __init__(
        self,
        service: AuthService
    ):
        self.service: AuthService = service

    @handle_error
    async def register(self, email, password):
        """
        Register a new user with the given email and password.
        """
        try:
            register = Register(email, password)
            result = await self.service.register(
                register.email,
                register.password
            )
            return result
        except ValidationError as e:
            raise str(e.json())

    @handle_error
    async def login(self, username, password):
        """
        Authenticate a user and provide access tokens.

        This endpoint authenticates a user using their email (username) and password,
        and returns access and refresh tokens upon successful authentication.
        """
        login_result = await self.service.login(username, password)
        return login_result

    @handle_error
    def verify_email(self):
        # TODO: verify_emailを実装する
        pass

    @handle_error
    def logout(self):
        # TODO: logoutを実装する
        pass

    @handle_error
    async def get_user(self, token: str):
        # TODO: ユーザー取得を実装する
        return await self.service.user(token)

    @handle_error
    async def update_user(
        self,
        user_id: str,
        email: str,
        is_superuser: bool,
        name: str,
        bio: str,
        profile_picture: str,
        token: str
    ):
        """
        Update the current user's profile information.

        This endpoint allows the authenticated user to update their profile information.
        """
        auth_user = self.service.user(token)

        if is_superuser is not None and not auth_user.is_superuser:
            raise R2RException(
                "Only superusers can update the superuser status of a user",
                403,
            )
        if not auth_user.is_superuser:
            if not auth_user.id == user_id:
                raise R2RException(
                    "Only superusers can update other users' information",
                    403,
                )

        return await self.service.update_user(
            user_id=user_id,
            email=email,
            is_superuser=is_superuser,
            name=name,
            bio=bio,
            profile_picture=profile_picture,
        )

    @handle_error
    def delete_user(self):
        # TODO: ユーザー削除を実装する
        pass

    @handle_error
    def refresh_access_token(self):
        # TODO: refresh_access_tokenを実装する
        pass

    @handle_error
    def change_password(self):
        # TODO: change_passwordを実装する
        pass

    @handle_error
    def request_password_reset(self):
        # TODO: request_password_resetを実装する
        pass

    @handle_error
    def reset_password(self):
        # TODO: reset_passwordを実装する
        pass
