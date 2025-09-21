import logging
from typing import Any

from ..agents.deep_dive_agent import generate_deep_dive_question
from ..agents.fast_eval_agent import fast_eval_answer
from ..agents.job_description_analyzer import analyze_job_description
from ..agents.question_retrieval import retrieve_question
from ..agents.resume_analyzer import analyze_resume
from ..agents.rubric_eval_agent import rubric_eval_answer
from .state import QuestionTurn, SessionState

logger = logging.getLogger(__name__)


# --- Analysis & Planning Nodes ---


def analyze_resume_node(state: SessionState) -> dict:
    """A node that analyzes the user's resume."""
    logger.info("--- Running Resume Analysis Node ---")
    resume_text = state.get("initial_resume_text")
    if not resume_text:
        logger.warning("No resume text found in state for analysis.")
        return {}
    analysis_result = analyze_resume(resume_text)
    return {"resume_summary": analysis_result.model_dump()}


def analyze_job_description_node(state: SessionState) -> dict:
    """A node that analyzes the provided job description."""
    logger.info("--- Running Job Description Analysis Node ---")
    job_desc_text = state.get("initial_job_description_text")
    if not job_desc_text:
        logger.warning("No job description text found in state for analysis.")
        return {}
    analysis_result = analyze_job_description(job_desc_text)
    return {"job_summary": analysis_result.model_dump()}


def create_interview_plan_node(state: SessionState) -> dict:
    """
    Creates a structured, dynamic interview plan based on the resume analysis.
    """
    logger.info("--- Creating Interview Plan ---")
    resume_summary = state.get("resume_summary")
    plan = ["introduction", "behavioral"]  # Always start with these

    if resume_summary:
        # Add deep dives for each project
        for project in resume_summary.get("projects", []):
            plan.append(f"deep_dive:project:{project['title']}")

        # Add deep dives for a few top skills
        for skill in resume_summary.get("skills", [])[:2]:  # Limit for brevity
            plan.append(f"deep_dive:skill:{skill['name']}")

    plan.append("technical:system_design")  # Add a generic technical question
    plan.append("wrap_up")

    logger.info(f"Generated Interview Plan: {plan}")
    return {"interview_plan": plan}


# --- Question Generation Nodes ---


def retrieve_question_node(state: SessionState) -> dict:
    """Retrieves a generic question from the vector store based on a topic."""
    logger.info("--- Running Question Retrieval Node ---")
    topic = state["current_topic"]

    question_output = retrieve_question(
        domain=topic,
        resume_analysis=state.get("resume_summary"),
        job_analysis=state.get("job_summary"),
    )
    turn = QuestionTurn(
        question_id=question_output.raw_question.question_id,
        conversational_text=question_output.conversational_text,
        raw_question_text=question_output.raw_question.text,
        ideal_answer_snippet=question_output.raw_question.ideal_answer_snippet,
    )
    return {"current_question": turn}


def deep_dive_question_node(state: SessionState) -> dict:
    """Generates a personalized, deep-dive question about a specific item."""
    logger.info("--- Running Deep Dive Question Node ---")
    topic_string = state["current_topic"]
    _, item_type, item_name = topic_string.split(":")
    resume_summary = state.get("resume_summary")

    question_output = generate_deep_dive_question(
        item_type=item_type, item_name=item_name, resume_summary=resume_summary
    )

    turn = QuestionTurn(
        question_id=None,
        conversational_text=question_output.conversational_text,
        raw_question_text=question_output.raw_question.text,
        ideal_answer_snippet=question_output.raw_question.ideal_answer_snippet,
    )
    return {"current_question": turn}


# --- Evaluation Nodes (Simplified with Reducer) ---


def fast_eval_node(state: SessionState) -> dict:
    """A node that performs a fast evaluation of the user's last answer."""
    logger.info("--- Running Fast Evaluation Node ---")
    current_question = state.get("current_question")
    if not current_question or not current_question.answer_text:
        logger.error("Fast eval error: required state is missing.")
        return {}

    eval_result = fast_eval_answer(
        question_text=current_question.raw_question_text,
        ideal_answer_snippet=current_question.ideal_answer_snippet,
        answer_text=current_question.answer_text,
    )
    # The reducer will handle merging this into the existing 'evals' dict
    return {"current_question": {"evals": {"fast_eval": eval_result.model_dump()}}}


def rubric_eval_node(state: SessionState) -> dict:
    """A node that performs a detailed, rubric-based evaluation."""
    logger.info("--- Running Rubric Evaluation Node ---")
    current_question = state.get("current_question")
    rubric = state.get("current_rubric")
    if not current_question or not current_question.answer_text or not rubric:
        logger.error("Rubric eval error: required state is missing.")
        return {}

    eval_result = rubric_eval_answer(
        question_text=current_question.raw_question_text,
        answer_text=current_question.answer_text,
        rubric=rubric,
    )
    # The reducer will handle merging this into the existing 'evals' dict
    return {"current_question": {"evals": {"rubric_eval": eval_result.model_dump()}}}


# --- Synthesis Node ---


def evaluation_synthesizer_node(state: SessionState) -> dict[str, Any]:
    """
    A non-LLM node that merges evaluations into a canonical score.
    """
    logger.info("--- Running Evaluation Synthesizer Node ---")
    current_question = state.get("current_question")
    if not current_question or not current_question.evals:
        logger.error("Synthesizer error: No evaluations found.")
        return {}

    fast_eval = current_question.evals.get("fast_eval")
    rubric_eval = current_question.evals.get("rubric_eval")
    if not fast_eval or not rubric_eval:
        logger.error("Synthesizer error: Missing fast_eval or rubric_eval.")
        return {}

    fast_score = fast_eval.get("score", 0)
    rubric_score = rubric_eval.get("aggregate_score", 0)
    canonical_score = (rubric_score * 0.7) + (fast_score * 0.3)

    canonical_eval = {
        "final_score": round(canonical_score, 2),
        "user_input_needed": rubric_eval.get("user_input_needed", False),
        "full_rubric": rubric_eval,
    }

    # The reducer will merge this final evaluation into the 'evals' dict
    return {"current_question": {"evals": {"canonical": canonical_eval}}}
