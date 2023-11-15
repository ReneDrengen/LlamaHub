"""
This module maintains the list of transformations that are supported by the system.
"""

from enum import Enum
from typing import Generic, Sequence, Type, TypeVar

from llama_index.bridge.pydantic import BaseModel, Field, GenericModel
from llama_index.embeddings import HuggingFaceEmbedding, OpenAIEmbedding
from llama_index.extractors import (
    EntityExtractor,
    KeywordExtractor,
    MarvinMetadataExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    TitleExtractor,
)
from llama_index.node_parser import (
    CodeSplitter,
    HierarchicalNodeParser,
    HTMLNodeParser,
    JSONNodeParser,
    MarkdownNodeParser,
    SentenceSplitter,
    SentenceWindowNodeParser,
    SimpleFileNodeParser,
    TokenTextSplitter,
)
from llama_index.schema import BaseComponent, BaseNode, Document


# Transform Input/Output Types
class TransformationIOType(BaseModel):
    name: str = Field(description="Name of the input/output type")
    description: str = Field(description="Description of the input/output type")
    python_type: str = Field(description="Python type of the input/output type")


class TransformationIOTypes(Enum):
    DOCUMENTS = TransformationIOType(
        name="Documents",
        description="A sequence of Documents",
        python_type=str(Sequence[Document]),
    )
    NODES = TransformationIOType(
        name="Nodes",
        description="A sequence of Nodes from a sequence of Documents",
        python_type=str(Sequence[BaseNode]),
    )


class TransformationCategory(BaseModel):
    """A description for a category of transformation within a pipeline."""

    name: str = Field(description="Unique name of the type of transformation")
    description: str = Field(description="Description for the type of transformation")
    input_type: TransformationIOType = Field(
        description="Input type for the transformation type"
    )
    output_type: TransformationIOType = Field(
        description="Output type for the transformation type"
    )


class TransformationCategories(Enum):
    """Supported transformation categories."""

    METADATA_EXTRACTOR = TransformationCategory(
        name="MetadataExtractor",
        description="Applies a function to extract metadata from nodes",
        input_type=TransformationIOTypes.NODES.value,
        output_type=TransformationIOTypes.NODES.value,
    )
    NODE_PARSER = TransformationCategory(
        name="NodeParser",
        description="Applies a function to parse nodes from documents",
        input_type=TransformationIOTypes.DOCUMENTS.value,
        output_type=TransformationIOTypes.NODES.value,
    )
    EMBEDDING = TransformationCategory(
        name="Embedding",
        description="Applies a function to embed nodes",
        input_type=TransformationIOTypes.NODES.value,
        output_type=TransformationIOTypes.NODES.value,
    )


class ConfigurableTransformation(BaseModel):
    """
    A class containing metadata for a type of transformation that can be in a pipeline.
    """

    name: str = Field(
        description="Unique and human-readable name for the type of transformation"
    )
    transformation_category: TransformationCategories = Field(
        description="Type of transformation"
    )
    component_type: Type[BaseComponent] = Field(
        description="Type of component that implements the transformation"
    )


class ConfigurableTransformations(Enum):
    """
    Enumeration of all supported ConfigurableTransformation instances.
    """

    ## Metadata Extractors
    KEYWORD_EXTRACTOR = ConfigurableTransformation(
        name="Keyword Extractor",
        transformation_category=TransformationCategories.METADATA_EXTRACTOR,
        component_type=KeywordExtractor,
    )
    TITLE_EXTRACTOR = ConfigurableTransformation(
        name="Title Extractor",
        transformation_category=TransformationCategories.METADATA_EXTRACTOR,
        component_type=TitleExtractor,
    )
    ENTITY_EXTRACTOR = ConfigurableTransformation(
        name="Entity Extractor",
        transformation_category=TransformationCategories.METADATA_EXTRACTOR,
        component_type=EntityExtractor,
    )
    MARVIN_METADATA_EXTRACTOR = ConfigurableTransformation(
        name="Marvin Metadata Extractor",
        transformation_category=TransformationCategories.METADATA_EXTRACTOR,
        component_type=MarvinMetadataExtractor,
    )
    SUMMARY_EXTRACTOR = ConfigurableTransformation(
        name="Summary Extractor",
        transformation_category=TransformationCategories.METADATA_EXTRACTOR,
        component_type=SummaryExtractor,
    )
    QUESTIONS_ANSWERED_EXTRACTOR = ConfigurableTransformation(
        name="Questions Answered Extractor",
        transformation_category=TransformationCategories.METADATA_EXTRACTOR,
        component_type=QuestionsAnsweredExtractor,
    )

    ## Node Parsers
    SENTENCE_WINDOW_NODE_PARSER = ConfigurableTransformation(
        name="Sentence Window Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=SentenceWindowNodeParser,
    )
    HIERARCHICAL_NODE_PARSER = ConfigurableTransformation(
        name="Hierarchical Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=HierarchicalNodeParser,
    )
    CODE_NODE_PARSER = ConfigurableTransformation(
        name="Code Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=CodeSplitter,
    )
    SENTENCE_AWARE_NODE_PARSER = ConfigurableTransformation(
        name="Sentence Splitter",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=SentenceSplitter,
    )
    TOKEN_AWARE_NODE_PARSER = ConfigurableTransformation(
        name="Token Text Splitter",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=TokenTextSplitter,
    )
    HTML_NODE_PARSER = ConfigurableTransformation(
        name="HTML Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=HTMLNodeParser,
    )
    MARKDOWN_NODE_PARSER = ConfigurableTransformation(
        name="Markdown Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=MarkdownNodeParser,
    )
    JSON_NODE_PARSER = ConfigurableTransformation(
        name="JSON Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=JSONNodeParser,
    )
    SIMPLE_FILE_NODE_PARSER = ConfigurableTransformation(
        name="Simple File Node Parser",
        transformation_category=TransformationCategories.NODE_PARSER,
        component_type=SimpleFileNodeParser,
    )

    ## Embeddings
    OPENAI_EMBEDDING = ConfigurableTransformation(
        name="OpenAI Embedding",
        transformation_category=TransformationCategories.EMBEDDING,
        component_type=OpenAIEmbedding,
    )
    HUGGINGFACE_EMBEDDING = ConfigurableTransformation(
        name="HuggingFace Embedding",
        transformation_category=TransformationCategories.EMBEDDING,
        component_type=HuggingFaceEmbedding,
    )

    @classmethod
    def from_component(cls, component: BaseComponent) -> "ConfigurableTransformations":
        component_class = type(component)
        for component_type in cls:
            if component_type.value.component_type == component_class:
                return component_type
        raise ValueError(
            f"Component {component} is not a supported transformation component."
        )

    def build_configured_transformation(
        self, component: BaseComponent
    ) -> "ConfiguredTransformation":
        component_type = self.value.component_type
        if not isinstance(component, component_type):
            raise ValueError(
                f"The enum value {self} is not compatible with component of "
                f"type {type(component)}"
            )
        return ConfiguredTransformation[component_type](  # type: ignore
            component=component, name=self.value.name
        )


T = TypeVar("T", bound=BaseComponent)


class ConfiguredTransformation(GenericModel, Generic[T]):
    """
    A class containing metadata & implementation for a transformation in a pipeline.
    """

    name: str
    component: T = Field(description="Component that implements the transformation")

    @classmethod
    def from_component(cls, component: BaseComponent) -> "ConfiguredTransformation":
        """
        Build a ConfiguredTransformation from a component.

        This should be the preferred way to build a ConfiguredTransformation
        as it will ensure that the component is supported as indicated by having a
        corresponding enum value in ConfigurableTransformations.

        This has the added bonus that you don't need to specify the generic type
        like ConfiguredTransformation[SentenceSplitter]. The return value of
        this ConfiguredTransformation.from_component(simple_node_parser) will be
        ConfiguredTransformation[SentenceSplitter] if simple_node_parser is
        a SentenceSplitter.
        """
        return ConfigurableTransformations.from_component(
            component
        ).build_configured_transformation(component)

    @property
    def configurable_transformation_type(self) -> ConfigurableTransformations:
        return ConfigurableTransformations.from_component(self.component)
