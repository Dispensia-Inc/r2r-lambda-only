import json
import logging
from typing import Optional, Union, List, Any
from uuid import UUID
from pydantic import BaseModel, ValidationError

from core.base import (
    GenerationConfig,
    GenericMessageResponse,
    R2RException
)
from core.base.api.models import UserResponse
from core.main.services.auth_service import AuthService
from core.main.services.retrieval_service import RetrievalService
from shared.abstractions.search import VectorSearchSettings, KGSearchSettings

logger = logging.getLogger()


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


class Services:
    auth: AuthService
    retrieval: RetrievalService


class LambdaOrchestration:
    def __init__(
        self,
        services: Services
    ):
        self.services: Services = services

    def _select_filters(
        self,
        auth_user: UserResponse,
        search_settings: Union[VectorSearchSettings, KGSearchSettings],
    ) -> dict[str, Any]:
        selected_collections = {
            str(cid) for cid in set(search_settings.selected_collection_ids)
        }

        if auth_user.is_superuser:
            if selected_collections:
                # For superusers, we only filter by selected collections
                filters = {
                    "collection_ids": {"$overlap": list(selected_collections)}
                }
            else:
                filters = {}
        else:
            user_collections = set(auth_user.collection_ids)

            if selected_collections:
                allowed_collections = user_collections.intersection(
                    selected_collections
                )
            else:
                allowed_collections = user_collections
            # for non-superusers, we filter by user_id and selected & allowed collections
            filters = {
                "$or": [
                    {"user_id": {"$eq": auth_user.id}},
                    {
                        "collection_ids": {
                            "$overlap": list(allowed_collections)
                        }
                    },
                ]  # type: ignore
            }

        if search_settings.filters != {}:
            # type: ignore
            filters = {"$and": [filters, search_settings.filters]}

        return filters

    @handle_error
    async def search(
        self,
        token: str,
        query: str,
        selected_collection_ids: List[UUID],
    ):
        auth_user = self.services.auth.user(token)

        vector_search_settings = VectorSearchSettings(
            use_hybrid_search=True,
            selected_collection_ids=selected_collection_ids,
        )

        # kg_searchは無効
        kg_search_settings = KGSearchSettings()

        vector_search_settings.filters = self._select_filters(
            auth_user, vector_search_settings
        )

        kg_search_settings.filters = self._select_filters(
            auth_user, kg_search_settings
        )

        response = await self.services.retrieval.search(
            query,
            vector_search_settings,
            kg_search_settings
        )
        return response.model_dump()
