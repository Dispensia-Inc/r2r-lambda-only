import base64
import logging
from typing import Optional, Union
from fastapi import Body, File, Form, Query, UploadFile
from pydantic import Json
from io import BytesIO
from uuid import UUID

from core.base import R2RException, generate_document_id
from core.main.services.ingestion_service import IngestionService

logger = logging.getLogger()


class LambdaOrchestration:
    def __init__(
        self,
        service: IngestionService
    ):
        self.service = service

    async def run(
        self,
        ingest_type=None,
        **kwargs
    ):
        if ingest_type == "ingest_files":
            return await self.ingest_files_app(**kwargs)
        elif ingest_type == "update_files":
            return await self.update_files_app(**kwargs)
        else:
            return False

    async def ingest_files_app(
        self,
        # TODO: FastAPIからじゃなくて引数から直接指定する
        files: list[UploadFile] = File(),
        document_ids: Optional[Json[list[UUID]]] = Form(None),
        metadatas: Optional[Json[list[dict]]] = Form(None),
        ingestion_config: Optional[Json[dict]] = Form(None),
        token="",
    ):
        # Tokenでログインする
        auth_user = self.service.providers.auth.user(token=token)

        # Check if the user is a superuser
        if not auth_user.is_superuser:
            for metadata in metadatas or []:
                if "user_id" in metadata and (
                    not auth_user.is_superuser
                    and metadata["user_id"] != str(auth_user.id)
                ):
                    raise R2RException(
                        status_code=403,
                        message="Non-superusers cannot set user_id in metadata.",
                    )
                # If user is not a superuser, set user_id in metadata
                metadata["user_id"] = str(auth_user.id)

        file_datas = await self._process_files(files)

        messages: list[dict[str, Union[str, None]]] = []
        for it, file_data in enumerate(file_datas):
            content_length = len(file_data["content"])
            file_content = BytesIO(base64.b64decode(file_data["content"]))

            file_data.pop("content", None)
            document_id = (
                document_ids[it]
                if document_ids
                else generate_document_id(
                    file_data["filename"], auth_user.id
                )
            )

            workflow_input = {
                "file_data": file_data,
                "document_id": str(document_id),
                "metadata": metadatas[it] if metadatas else None,
                "ingestion_config": ingestion_config,
                "user": auth_user.model_dump_json(),
                "size_in_bytes": content_length,
                "is_update": False,
            }

            file_name = file_data["filename"]
            # ファイルをDBに保存する
            await self.service.providers.file.store_file(
                document_id,
                file_name,
                file_content,
                file_data["content_type"],
            )

            logger.info(
                f"Running ingestion without orchestration for file {
                    file_name} and document_id {document_id}."
            )

            from core.main.orchestration import (
                simple_ingestion_factory,
            )

            # ベクトルデータをDBに保存？
            simple_ingestor = simple_ingestion_factory(self.service)
            await simple_ingestor["ingest-files"](workflow_input)
            messages.append(
                {
                    "message": "Ingestion task completed successfully.",
                    "document_id": str(document_id),
                    "task_id": None,
                }
            )

        return messages  # type: ignore

    async def update_files_app(
        self,
        files: list[UploadFile] = File(),
        document_ids: Optional[Json[list[UUID]]] = Form(None),
        metadatas: Optional[Json[list[dict]]] = Form(None),
        ingestion_config: Optional[Json[dict]] = Form(None),
        token="",
    ):
        # Tokenでログインする
        auth_user = self.service.providers.auth.user(token=token)

        if not auth_user.is_superuser:
            for metadata in metadatas or []:
                if "user_id" in metadata and metadata["user_id"] != str(
                    auth_user.id
                ):
                    raise R2RException(
                        status_code=403,
                        message="Non-superusers cannot set user_id in metadata.",
                    )
                metadata["user_id"] = str(auth_user.id)

        file_datas = await self._process_files(files)

        processed_data = []
        for it, file_data in enumerate(file_datas):
            content = base64.b64decode(file_data.pop("content"))
            document_id = (
                document_ids[it]
                if document_ids
                else generate_document_id(
                    file_data["filename"], auth_user.id
                )
            )

            await self.service.providers.file.store_file(
                document_id,
                file_data["filename"],
                BytesIO(content),
                file_data["content_type"],
            )

            processed_data.append(
                {
                    "file_data": file_data,
                    "file_length": len(content),
                    "document_id": str(document_id),
                }
            )

        workflow_input = {
            "file_datas": [item["file_data"] for item in processed_data],
            "file_sizes_in_bytes": [
                item["file_length"] for item in processed_data
            ],
            "document_ids": [
                item["document_id"] for item in processed_data
            ],
            "metadatas": metadatas,
            "ingestion_config": ingestion_config,
            "user": auth_user.model_dump_json(),
            "is_update": True,
        }

        logger.info("Running update without orchestration.")

        from core.main.orchestration import simple_ingestion_factory

        simple_ingestor = simple_ingestion_factory(self.service)
        await simple_ingestor["update-files"](workflow_input)
        return {  # type: ignore
            "message": "Update task completed successfully.",
            "document_ids": workflow_input["document_ids"],
            "task_id": None,
        }

    @staticmethod
    async def _process_files(files):
        import base64

        file_datas = []
        for file in files:
            content = await file.read()
            file_datas.append(
                {
                    "filename": file.filename,
                    # contentはbyte型
                    "content": base64.b64encode(content).decode("utf-8"),
                    "content_type": file.content_type,
                }
            )
        return file_datas
