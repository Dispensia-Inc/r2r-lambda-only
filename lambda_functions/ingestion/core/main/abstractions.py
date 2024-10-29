from core.main.abstractions import R2RProviders, R2RPipes
from core.base.pipes import AsyncPipe


class CustomR2RPipes(R2RPipes):
    parsing_pipe: AsyncPipe | None
    embedding_pipe: AsyncPipe | None
    kg_search_pipe: AsyncPipe | None
    kg_triples_extraction_pipe: AsyncPipe | None
    kg_storage_pipe: AsyncPipe | None
    kg_entity_description_pipe: AsyncPipe | None
    kg_clustering_pipe: AsyncPipe | None
    kg_entity_deduplication_pipe: AsyncPipe | None
    kg_entity_deduplication_summary_pipe: AsyncPipe | None
    kg_community_summary_pipe: AsyncPipe | None
    kg_prompt_tuning_pipe: AsyncPipe | None
    rag_pipe: AsyncPipe | None
    streaming_rag_pipe: AsyncPipe | None
    vector_storage_pipe: AsyncPipe | None
    vector_search_pipe: AsyncPipe | None