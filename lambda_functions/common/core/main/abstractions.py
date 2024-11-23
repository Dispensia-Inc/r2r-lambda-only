from core.main.abstractions import R2RProviders
from ...core.providers.auth.cognito import CognitoAuthProvider


class CustomR2RProviders(R2RProviders):
    auth: CognitoAuthProvider
