from pydantic import BaseModel

from lambda_functions.ingestion.core.base import (
    AsyncPipe,
)


# TODO: R2RProviders不要部分の削除
class R2RProviders(BaseModel):
    auth: AuthProvider
    database: DatabaseProvider
    ingestion: IngestionProvider
    embedding: EmbeddingProvider
    file: FileProvider
    llm: CompletionProvider
    orchestration: OrchestrationProvider
    prompt: PromptProvider

    class Config:
        arbitrary_types_allowed = True


class R2RPipes(BaseModel):
    parsing_pipe: AsyncPipe
    embedding_pipe: AsyncPipe
    vector_storage_pipe: AsyncPipe

    class Config:
        arbitrary_types_allowed = True