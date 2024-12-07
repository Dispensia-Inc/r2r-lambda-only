import logging
from typing import Union, List, Any
from uuid import UUID

from lambda_functions.common.core.main.exception import LambdaException
from core.base.api.models import UserResponse
from core.main.services.auth_service import AuthService
from core.main.services.retrieval_service import RetrievalService
from shared.abstractions.search import VectorSearchSettings, KGSearchSettings
from core.base import R2RException
from core.main.services.management_service import ManagementService

logger = logging.getLogger()


def handle_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            logger.error(f"handle_error: {err}")
            raise LambdaException(err, 500)
        except AttributeError as err:
            logger.error(f"handle_error: {err}")
            raise LambdaException(err, 500)
    return inner


class LambdaOrchestration:
    def __init__(
        self,
        auth: AuthService,
        service: ManagementService,
        retrieval: RetrievalService
    ):
        self.auth_service = auth
        self.retrieval_service = retrieval
        self.service: ManagementService = service

    @handle_error
    async def create_collection(
        self,
        token: str,
        name: str,
        description: str,
    ):
        auth_user = await self.auth_service.user(token)

        collection_id = await self.service.create_collection(
            name, description
        )
        await self.service.add_user_to_collection(  # type: ignore
            auth_user.id, collection_id.collection_id
        )
        return collection_id

    @handle_error
    async def update_collection(
        self,
        token: str,
        collection_id: UUID,
        name: str,
        description: str,
    ):
        auth_user = await self.auth_service.user(token)
        collection_uuid = UUID(collection_id)
        
        if (
            not auth_user.is_superuser
            and collection_uuid not in auth_user.collection_ids
        ):
            raise R2RException(
                "The currently authenticated user does not have access to the specified collection.",
                403,
            )

        return await self.service.update_collection(  # type: ignore
            collection_uuid, name, description
        )

    @handle_error
    async def get_collection(
        self,
        token: str,
        collection_id: UUID,
    ):
        auth_user = await self.auth_service.user(token)
        collection_uuid = UUID(collection_id)
        if (
            not auth_user.is_superuser
            and collection_uuid not in auth_user.collection_ids
        ):
            raise R2RException(
                "The currently authenticated user does not have access to the specified collection.",
                403,
            )

        result = await self.service.get_collection(collection_uuid)
        return result  # type: ignore
    
    @handle_error
    async def delete_collection(
        self,
        token: str,
        collection_id: UUID,
    ):
        auth_user = await self.auth_service.user(token)
        collection_uuid = UUID(collection_id)
        
        if (
            not auth_user.is_superuser
            and collection_uuid not in auth_user.collection_ids
        ):
            raise R2RException(
                "The currently authenticated user does not have access to the specified collection.",
                403,
            )

        return await self.service.delete_collection(collection_uuid)
    
    @handle_error
    async def add_user_to_collection(
        self,
        token: str,
        user_id: UUID,
        collection_id: UUID,
    ):
        auth_user = await self.auth_service.user(token)
        
        collection_uuid = UUID(collection_id)
        
        user_uuid = UUID(user_id)
        if (
            not auth_user.is_superuser
            and collection_uuid not in auth_user.collection_ids
        ):
            raise R2RException(
                "The currently authenticated user does not have access to the specified collection.",
                403,
            )

        result = await self.service.add_user_to_collection(
            user_uuid, collection_uuid
        )
        return result  # type: ignore
    
    @handle_error
    async def remove_user_from_collection(
        self,
        token: str,
        user_id: UUID,
        collection_id: UUID,
    ):
        auth_user = await self.auth_service.user(token)
        
        collection_uuid = UUID(collection_id)
        
        user_uuid = UUID(user_id)
        if (
            not auth_user.is_superuser
            and collection_uuid not in auth_user.collection_ids
        ):
            raise R2RException(
                "The currently authenticated user does not have access to the specified collection.",
                403,
            )

        await self.service.remove_user_from_collection(
            user_uuid, collection_uuid
        )
        return None  # type: ignore
    
    @handle_error
    async def user_collections(
        self,
        token: str,
        user_id: UUID,
        offset: int,
        limit: int,
    ):
        auth_user = await self.auth_service.user(token)
        
        if str(auth_user.id) != user_id and not auth_user.is_superuser:
            raise R2RException(
                "The currently authenticated user does not have access to the specified collection.",
                403,
            )
        user_uuid = UUID(user_id)
        user_collection_response = (
            await self.service.get_collections_for_user(
                user_uuid, offset, limit
            )
        )

        return user_collection_response["results"], {  # type: ignore
            "total_entries": user_collection_response["total_entries"]
        }