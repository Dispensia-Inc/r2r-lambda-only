import logging
from typing import Union, List, Any
from uuid import UUID

from lambda_functions.common.core.main.exception import LambdaException
from core.base.api.models import UserResponse
from core.main.services.auth_service import AuthService
from core.main.services.retrieval_service import RetrievalService
from shared.abstractions.search import VectorSearchSettings, KGSearchSettings

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
        retrieval: RetrievalService
    ):
        self.auth_service = auth
        self.retrieval_service = retrieval

    @handle_error
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
        selected_collection_ids: List[UUID] = [],
    ):
        auth_user = await self.auth_service.user(token)

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

        response = await self.retrieval_service.search(
            query,
            vector_search_settings,
            kg_search_settings
        )
        return response
