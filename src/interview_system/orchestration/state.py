from datetime import datetime
from typing import Annotated, Any, TypedDict
from uuid import UUID

from pydantic import BaseModel, Field


# Using Pydantic for QuestionTurn to get validation within the list
class QuestionTurn(BaseModel):
    question_id: str | None = None
    conversational_text: str
    raw_question_text: str
    ideal_answer_snippet: str | None = None
    answer_text: str | None = None
    answer_audio_ref: str | None = None
    evals: dict[str, Any] = Field(default_factory=dict)
    feedback: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def merge_question_updates(
    left: QuestionTurn | None, right: QuestionTurn | dict | None
) -> QuestionTurn | None:
    """
    Reducer function to merge updates to the current_question.
    Primarily merges the 'evals' dictionaries from parallel evaluation nodes.
    """
    if left is None:
        return (
            right
            if isinstance(right, QuestionTurn) or right is None
            else QuestionTurn(**right)
        )
    if right is None:
        return left

    right_dict = right.model_dump() if isinstance(right, QuestionTurn) else right
    merged = left.model_copy(deep=True)

    # Merge the 'evals' dictionaries
    if "evals" in right_dict and right_dict["evals"]:
        merged.evals.update(right_dict["evals"])

    # Allow other fields to be updated
    for key, value in right_dict.items():
        if key != "evals" and value is not None:
            setattr(merged, key, value)

    return merged


# Using TypedDict for the main graph state is standard for LangGraph
class SessionState(TypedDict):
    session_id: UUID
    user_id: UUID
    initial_resume_text: str | None
    initial_job_description_text: str | None
    current_rubric: dict | None

    resume_summary: dict | None
    job_summary: dict | None
    
    # This plan guides the high-level flow of the interview
    interview_plan: list[str]

    question_history: list[QuestionTurn]
    
    # ANNOTATED KEY: This applies the reducer to the current_question field
    current_question: Annotated[
        QuestionTurn | None,
        merge_question_updates,
    ]
    
    personalization_profile: dict | None

