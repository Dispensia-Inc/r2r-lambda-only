from typing import Union

from core.base import (
    IngestionProvider,
)
from core.main.abstractions import R2RProviders
from core.providers import (
    R2RIngestionProvider,
    R2RAuthProvider,
    SupabaseAuthProvider,
    UnstructuredIngestionProvider
)

from ...core.providers.auth.cognito import CognitoAuthProvider


class CustomR2RProviders(R2RProviders):
    auth: Union[R2RAuthProvider, SupabaseAuthProvider, CognitoAuthProvider]
    ingestion: Union[R2RIngestionProvider,
                     UnstructuredIngestionProvider, IngestionProvider]
