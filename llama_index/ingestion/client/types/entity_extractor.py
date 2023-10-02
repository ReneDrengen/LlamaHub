# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime
from .metadata_mode import MetadataMode


class EntityExtractor(pydantic.BaseModel):
    """
    Entity extractor. Extracts `entities` into a metadata field using a default model
    `tomaarsen/span-marker-mbert-base-multinerd` and the SpanMarker library.

    Install SpanMarker with `pip install span-marker`.
    """

    is_text_node_only: typing.Optional[bool]
    show_progress: typing.Optional[bool]
    metadata_mode: typing.Optional[MetadataMode]
    model_name: typing.Optional[str] = pydantic.Field(
        description="The model name of the SpanMarker model to use."
    )
    prediction_threshold: typing.Optional[float] = pydantic.Field(
        description="The confidence threshold for accepting predictions."
    )
    span_joiner: str = pydantic.Field(description="The seperator beween entity names.")
    label_entities: typing.Optional[bool] = pydantic.Field(
        description="Include entity class labels or not."
    )
    device: typing.Optional[str] = pydantic.Field(
        description="Device to run model on, i.e. 'cuda', 'cpu'"
    )
    entity_map: typing.Optional[typing.Dict[str, str]] = pydantic.Field(
        description="Mapping of entity class names to usable names."
    )
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
