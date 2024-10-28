
# TODO: R2RProviders不要部分の削除
class R2RProviders(BaseModel):
    auth: AuthProvider
    database: DatabaseProvider
    ingestion: IngestionProvider
    embedding: EmbeddingProvider
    file: FileProvider
    kg: KGProvider
    llm: CompletionProvider
    orchestration: OrchestrationProvider
    prompt: PromptProvider

    class Config:
        arbitrary_types_allowed = True


# TODO: R2RPipes不要部分削除
class R2RPipes(BaseModel):
    parsing_pipe: AsyncPipe
    embedding_pipe: AsyncPipe
    kg_search_pipe: AsyncPipe
    kg_triples_extraction_pipe: AsyncPipe
    kg_storage_pipe: AsyncPipe
    kg_entity_description_pipe: AsyncPipe
    kg_clustering_pipe: AsyncPipe
    kg_entity_deduplication_pipe: AsyncPipe
    kg_entity_deduplication_summary_pipe: AsyncPipe
    kg_community_summary_pipe: AsyncPipe
    kg_prompt_tuning_pipe: AsyncPipe
    rag_pipe: AsyncPipe
    streaming_rag_pipe: AsyncPipe
    vector_storage_pipe: AsyncPipe
    vector_search_pipe: AsyncPipe

    class Config:
        arbitrary_types_allowed = True