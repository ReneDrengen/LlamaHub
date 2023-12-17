"""Labelled Evaluation Class."""

import asyncio
import time
from typing import List, Optional, Union

from pandas import DataFrame as PandasDataFrame

from llama_index.bridge.pydantic import Field
from llama_index.evaluation import (
    BaseEvaluator,
    EvaluationResult,
    InvalidEvaluationResult,
    PairwiseComparisonEvaluator,
)
from llama_index.evaluation.pairwise import EvaluationSource
from llama_index.llama_dataset.base import (
    BaseLlamaDataExample,
    BaseLlamaDataset,
    BaseLlamaExamplePrediction,
    BaseLlamaPredictionDataset,
    CreatedBy,
)


class EvaluationExamplePrediction(BaseLlamaExamplePrediction):
    """Evaluation example prediction class.

    Args:
        feedback (Optional[str]): The evaluator's feedback.
        score (Optional[float]): The evaluator's score.
    """

    feedback: str = Field(
        default_factory=str,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    score: Optional[float] = Field(
        default=None,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    invalid_prediction: bool = Field(
        default=False, description="Whether or not the prediction is a valid one."
    )
    invalid_reason: Optional[str] = Field(
        default=None, description="Reason as to why prediction is invalid."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "EvaluationExamplePrediction"


class LabelledEvaluationDataExample(BaseLlamaDataExample):
    """Evaluation example class.

    This data class contains the ingredients to perform a new "prediction" i.e.,
    evaluation. Here an evaluator is meant to evaluate a response against an
    associated query as well as optionally contexts.

    Args:
        query (str): The user query
        query_by (CreatedBy): Query generated by human or ai (model-name)
        contexts (Optional[List[str]]): The contexts used for response
        answer (str): Answer to the query that is to be evaluated.
        answer_by: The reference answer generated by human or ai (model-name).
        ground_truth_answer (Optional[str]):
        ground_truth_answer_by (Optional[CreatedBy]):
        reference_feedback (str): The reference feedback evaluation.
        reference_score (float): The reference score evaluation.
        reference_evaluation_by (CreatedBy): Evaluation generated by human or ai (model-name)
    """

    query: str = Field(
        default_factory=str, description="The user query for the example."
    )
    query_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the query."
    )
    contexts: Optional[List[str]] = Field(
        default_factory=None,
        description="The contexts used to generate the answer.",
    )
    answer: str = Field(
        default_factory=str,
        description="The provided answer to the example that is to be evaluated.",
    )
    answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the answer."
    )
    ground_truth_answer: Optional[str] = Field(
        default=None,
        description="The ground truth answer to the example that is used to evaluate the provided `answer`.",
    )
    ground_truth_answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the ground-truth answer."
    )
    reference_feedback: Optional[str] = Field(
        default=None,
        description="The reference feedback (ground-truth).",
    )
    reference_score: float = Field(
        default_factory=float, description="The reference score (ground-truth)."
    )
    reference_evaluation_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the evaluation (feedback and score)."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "LabelledEvaluationDataExample"


class EvaluationPredictionDataset(BaseLlamaPredictionDataset):
    """Evaluation Prediction Dataset Class."""

    _prediction_type = EvaluationExamplePrediction

    def to_pandas(self) -> PandasDataFrame:
        """Create pandas dataframe."""
        data = {}
        if self.predictions:
            data = {
                "feedback": [t.feedback for t in self.predictions],
                "score": [t.score for t in self.predictions],
            }

        return PandasDataFrame(data)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "EvaluationPredictionDataset"


class LabelledEvaluationDataset(BaseLlamaDataset):
    """LabelledEvalationDataset class."""

    _example_type = LabelledEvaluationDataExample

    def to_pandas(self) -> PandasDataFrame:
        """Create pandas dataframe."""
        data = {
            "query": [t.query for t in self.examples],
            "answer": [t.answer for t in self.examples],
            "contexts": [t.contexts for t in self.examples],
            "ground_truth_answer": [t.ground_truth_answer for t in self.examples],
            "query_by": [str(t.query_by) for t in self.examples],
            "answer_by": [str(t.answer_by) for t in self.examples],
            "ground_truth_answer_by": [
                str(t.ground_truth_answer_by) for t in self.examples
            ],
            "reference_feedback": [t.reference_feedback for t in self.examples],
            "reference_score": [t.reference_score for t in self.examples],
            "reference_evaluation_by": [
                t.reference_evaluation_by for t in self.examples
            ],
        }

        return PandasDataFrame(data)

    async def _apredict_example(
        self,
        evaluator: BaseEvaluator,
        example: LabelledEvaluationDataExample,
        sleep_time_in_seconds: int,
    ) -> EvaluationExamplePrediction:
        """Async predict RAG example with a query engine."""
        await asyncio.sleep(sleep_time_in_seconds)
        eval_kwargs = {
            "query": example.query,
            "response": example.answer,
            "contexts": example.contexts,
            "reference": example.ground_truth_answer,
            "sleep_time_in_seconds": sleep_time_in_seconds,
        }
        eval_result: Union[
            EvaluationResult, InvalidEvaluationResult
        ] = await evaluator.aevaluate(**eval_kwargs)
        return EvaluationExamplePrediction(
            feedback=eval_result.feedback, score=eval_result.score
        )

    def _predict_example(
        self,
        evaluator: BaseEvaluator,
        example: LabelledEvaluationDataExample,
        sleep_time_in_seconds: int = 0,
    ) -> EvaluationExamplePrediction:
        """Predict RAG example with a query engine."""
        time.sleep(sleep_time_in_seconds)
        eval_kwargs = {
            "query": example.query,
            "response": example.answer,
            "contexts": example.contexts,
            "reference": example.ground_truth_answer,
            "sleep_time_in_seconds": sleep_time_in_seconds,
        }
        eval_result: EvaluationResult = evaluator.evaluate(**eval_kwargs)
        return EvaluationExamplePrediction(
            feedback=eval_result.feedback, score=eval_result.score
        )

    def _construct_prediction_dataset(
        self, predictions: List[EvaluationExamplePrediction]
    ) -> EvaluationPredictionDataset:
        """Construct prediction dataset."""
        return EvaluationPredictionDataset(predictions=predictions)

    def class_name(self) -> str:
        """Class name."""
        return "LabelledEvaluationDataset"


class PairwiseEvaluationExamplePrediction(BaseLlamaExamplePrediction):
    """Pairwise evaluation example prediction class.

    Args:
        feedback (Optional[str]): The evaluator's feedback.
        score (Optional[float]): The evaluator's score.
        evaluation_source (EvaluationSource): If the evaluation came from original order or flipped; or inconclusive.
    """

    feedback: str = Field(
        default_factory=str,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    score: Optional[float] = Field(
        default=None,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    evaluation_source: Optional[EvaluationSource] = Field(
        default=None,
        description=(
            "Whether the evaluation comes from original, or flipped ordering. Can also be neither here indicating inconclusive judgement."
        ),
    )
    invalid_prediction: bool = Field(
        default=False, description="Whether or not the prediction is a valid one."
    )
    invalid_reason: Optional[str] = Field(
        default=None, description="Reason as to why prediction is invalid."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "PairwiseEvaluationExamplePrediction"


class PairwiseEvaluationPredictionDataset(BaseLlamaPredictionDataset):
    """Pairwise evaluation predictions dataset class."""

    _prediction_type = PairwiseEvaluationExamplePrediction

    def to_pandas(self) -> PandasDataFrame:
        """Create pandas dataframe."""
        data = {}
        if self.predictions:
            data = {
                "feedback": [t.feedback for t in self.predictions],
                "score": [t.score for t in self.predictions],
                "ordering": [t.evaluation_source.value for t in self.predictions],
            }

        return PandasDataFrame(data)

    def class_name(self) -> str:
        """Class name."""
        return "PairwiseEvaluationPredictionDataset"


class LabelledPairwiseEvaluationDataExample(LabelledEvaluationDataExample):
    """Labelled pairwise evaluation data example class."""

    second_answer: str = Field(
        default_factory=str,
        description="The second answer to the example that is to be evaluated along versus `answer`.",
    )
    second_answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the second answer."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "LabelledPairwiseEvaluationDataExample"


class LabelledPairwiseEvaluationDataset(BaseLlamaDataset):
    """Labelled pairwise evaluation dataset. For evaluating the evaluator in
    performing pairwise evaluations.

    Args:
        BaseLlamaDataset (_type_): _description_
    """

    _example_type = LabelledPairwiseEvaluationDataExample

    def to_pandas(self) -> PandasDataFrame:
        """Create pandas dataframe."""
        data = {
            "query": [t.query for t in self.examples],
            "answer": [t.answer for t in self.examples],
            "second_answer": [t.second_answer for t in self.examples],
            "contexts": [t.contexts for t in self.examples],
            "ground_truth_answer": [t.ground_truth_answer for t in self.examples],
            "query_by": [str(t.query_by) for t in self.examples],
            "answer_by": [str(t.answer_by) for t in self.examples],
            "second_answer_by": [str(t.second_answer_by) for t in self.examples],
            "ground_truth_answer_by": [
                str(t.ground_truth_answer_by) for t in self.examples
            ],
            "reference_feedback": [t.reference_feedback for t in self.examples],
            "reference_score": [t.reference_score for t in self.examples],
            "reference_evaluation_by": [
                t.reference_evaluation_by for t in self.examples
            ],
        }

        return PandasDataFrame(data)

    async def _apredict_example(
        self,
        evaluator: PairwiseComparisonEvaluator,
        example: LabelledPairwiseEvaluationDataExample,
        sleep_time_in_seconds: int,
    ) -> PairwiseEvaluationExamplePrediction:
        """Async predict evaluation example with an Evaluator."""
        await asyncio.sleep(sleep_time_in_seconds)
        eval_result: Union[
            InvalidEvaluationResult, EvaluationResult
        ] = await evaluator.aevaluate(
            query=example.query,
            response=example.answer,
            second_response=example.second_answer,
            contexts=example.contexts,
            reference=example.ground_truth_answer,
            sleep_time_in_seconds=sleep_time_in_seconds,
        )
        if isinstance(eval_result, EvaluationResult):
            return PairwiseEvaluationExamplePrediction(
                feedback=eval_result.feedback,
                score=eval_result.score,
                evaluation_source=eval_result.pairwise_source,
            )
        else:
            return PairwiseEvaluationExamplePrediction(
                invalid_prediction=True, invalid_reason=eval_result.invalid_reason
            )

    def _predict_example(
        self,
        evaluator: PairwiseComparisonEvaluator,
        example: LabelledPairwiseEvaluationDataExample,
        sleep_time_in_seconds: int = 0,
    ) -> PairwiseEvaluationExamplePrediction:
        """Predict RAG example with a query engine."""
        time.sleep(sleep_time_in_seconds)
        eval_kwargs = {
            "query": example.query,
            "response": example.answer,
            "second_response": example.second_answer,
            "contexts": example.contexts,
            "reference": example.ground_truth_answer,
            "sleep_time_in_seconds": sleep_time_in_seconds,
        }
        eval_result: EvaluationResult = evaluator.evaluate(**eval_kwargs)
        return PairwiseEvaluationExamplePrediction(
            feedback=eval_result.feedback,
            score=eval_result.score,
            evaluation_source=eval_result.pairwise_source,
        )

    def _construct_prediction_dataset(
        self, predictions: List[PairwiseEvaluationExamplePrediction]
    ) -> PairwiseEvaluationPredictionDataset:
        """Construct prediction dataset."""
        return PairwiseEvaluationPredictionDataset(predictions=predictions)

    def class_name(self) -> str:
        """Class name."""
        return "PairwiseEvaluationPredictionDataset"


# British English + American English
LabeledEvaluationDataExample = LabelledEvaluationDataExample
LabeledEvaluationDataset = LabelledEvaluationDataset
LabeledPairwiseEvaluationDataExample = LabelledPairwiseEvaluationDataExample
LabeledPairwiseEvaluationDataset = LabelledPairwiseEvaluationDataset
