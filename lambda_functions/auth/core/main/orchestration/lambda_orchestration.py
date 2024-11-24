import json
import logging
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ValidationError

from core.base.api.models import (
    GenericMessageResponse
)
from core.base import R2RException
from core.main.services.auth_service import AuthService

logger = logging.getLogger()


class Register(BaseModel):
    email: str
    password: str


class LambdaException(Exception):
    def __init__(self, status_code: int, error_msg: str):
        self.status_code = status_code
        self.error_msg = error_msg

    def __str__(self):
        obj = {
            "statusCode": self.status_code,
            "errorMessage": self.error_msg
        }
        return json.dumps(obj)


def handle_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            logger.error(str(err))
            raise LambdaException(500, err["errorMessage"])
    return inner


class LambdaOrchestration:
    def __init__(
        self,
        service: AuthService
    ):
        self.service: AuthService = service

    @handle_error
    async def get_user(self, token: str):
        user = await self.service.user(token)
        return user.to_dict()
