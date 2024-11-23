from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ValidationError

from core.base.api.models import (
    GenericMessageResponse
)
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
        メールアドレスとパスワードで新しいユーザーを作成する
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
        ユーザーを認証してアクセストークンを返す

        This endpoint authenticates a user using their email (username) and password,
        and returns access and refresh tokens upon successful authentication.
        """
        login_result = await self.service.login(username, password)
        return login_result

    @handle_error
    async def verify_email(self, email: str, verification_code: str):
        """
        メールアドレスを確認する

        This endpoint is used to confirm a user's email address using the verification code
        sent to their email after registration.
        """
        result = await self.service.verify_email(email, verification_code)
        return GenericMessageResponse(message=result["message"])

    @handle_error
    async def logout(self, token: str):
        """
        現在のユーザーをログアウトする

        This endpoint invalidates the user's current access token, effectively logging them out.
        """
        result = await self.service.logout(token)
        return GenericMessageResponse(message=result["message"])

    @handle_error
    async def get_user(self, token: str):
        if token:
            return await self.service.user(token)
        else:
            GenericMessageResponse(message="error: The token was not found.")

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
        現在のユーザープロフィール情報を更新する

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
    async def delete_user(
            self,
            user_id: str,
            password: Optional[str],
            token: str,
            # ユーザーのベクトルデータを削除するかどうか
            delete_vector_data: Optional[bool] = False):
        """
        ユーザーアカウントを削除する

        This endpoint allows users to delete their own account or, for superusers,
        to delete any user account.
        """
        auth_user = self.service.user(token)
        if str(auth_user.id) != user_id and not auth_user.is_superuser:
            raise Exception("User ID does not match authenticated user")
        if not auth_user.is_superuser and not password:
            raise Exception("Password is required for non-superusers")
        user_uuid = UUID(user_id)
        result = await self.service.delete_user(
            user_uuid, password, delete_vector_data
        )
        return GenericMessageResponse(message=result["message"])

    @handle_error
    async def refresh_access_token(self, refresh_token: str):
        """
        リフレッシュトークンを使ってアクセストークンをリフレッシュする

        This endpoint allows users to obtain a new access token using their refresh token.
        """
        refresh_result = await self.service.refresh_access_token(
            refresh_token=refresh_token,
        )
        return refresh_result

    @handle_error
    async def change_password(self, current_password: str, new_password: str, token: str):
        """
        認証済みユーザーのパスワードを変更する

        This endpoint allows users to change their password by providing their current password
        and a new password.
        """
        auth_user = self.service.user(token)
        result = await self.service.change_password(
            auth_user,
            current_password,
            new_password,
        )
        return GenericMessageResponse(message=result["message"])

    @handle_error
    async def request_password_reset(self, email: str):
        """
        Request a password reset for a user.

        This endpoint initiates the password reset process by sending a reset link
        to the specified email address.
        """
        result = await self.service.request_password_reset(email)
        return GenericMessageResponse(message=result["message"])

    @handle_error
    async def reset_password(self, reset_token: str, new_password: str):
        result = await self.service.confirm_password_reset(
            reset_token, new_password
        )
        return GenericMessageResponse(message=result["message"])
