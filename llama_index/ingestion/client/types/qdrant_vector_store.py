# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime


class QdrantVectorStore(pydantic.BaseModel):
    """
    Qdrant Vector Store.

    In this vector store, embeddings and docs are stored within a
    Qdrant collection.

    During query time, the index uses Qdrant to query for the top
    k most similar nodes.

    Args:
        collection_name: (str): name of the Qdrant collection
        client (Optional[Any]): QdrantClient instance from `qdrant-client` package
    """

    stores_text: typing.Optional[bool]
    is_embedding_query: typing.Optional[bool]
    flat_metadata: typing.Optional[bool]
    collection_name: str
    url: typing.Optional[str]
    api_key: typing.Optional[str]
    batch_size: int
    client_kwargs: typing.Optional[typing.Dict[str, typing.Any]]
    class_name: typing.Optional[str]

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {
            "by_alias": True,
            "exclude_unset": True,
            **kwargs,
        }
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {
            "by_alias": True,
            "exclude_unset": True,
            **kwargs,
        }
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        json_encoders = {dt.datetime: serialize_datetime}
