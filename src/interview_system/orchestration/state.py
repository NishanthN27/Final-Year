from datetime import datetime
from typing import Annotated, Any, TypedDict

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
    Reducer function to robustly merge updates to the current_question.
    It handles both full object updates and partial, nested updates from parallel nodes.
    """
    # If the new update is None, it means we are explicitly clearing the question.
    if right is None:
        return None

    # If there is no existing question, create a new one from the update.
    if left is None:
        return QuestionTurn(**right) if isinstance(right, dict) else right

    # This branch handles UPDATES to an existing QuestionTurn object
    right_dict = right.model_dump() if isinstance(right, QuestionTurn) else right
    merged = left.model_copy(deep=True)

    # Deep merge the 'evals' and 'feedback' dictionaries
    if "evals" in right_dict and right_dict["evals"]:
        merged.evals.update(right_dict["evals"])
    if "feedback" in right_dict and right_dict["feedback"]:
        merged.feedback.update(right_dict["feedback"])

    # Update any other top-level fields from the new update
    for key, value in right_dict.items():
        if key not in ["evals", "feedback"] and value is not None:
            setattr(merged, key, value)

    return merged


# Using TypedDict for the main graph state is standard for LangGraph
class SessionState(TypedDict):
    session_id: str
    user_id: str
    initial_resume_text: str | None
    initial_job_description_text: str | None
    current_rubric: dict | None

    # ADDED: This field is set by the topic_setter node and read by the main router.
    current_topic: str | None

    # ADDED: This field holds the output of the final report_generator node.
    final_report: dict | None

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
