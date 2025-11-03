# src/interview_system/orchestration/nodes.py

import logging
from typing import Any
from contextlib import contextmanager

from ..agents.deep_dive_agent import generate_deep_dive_question
from ..agents.fast_eval_agent import fast_eval_answer
from ..agents.feedback_generator import generate_feedback
from ..agents.follow_up_agent import generate_follow_up
from ..agents.interview_plan_agent import generate_interview_plan
from ..agents.job_description_analyzer import analyze_job_description
from ..agents.personalization_agent import create_personalization_plan
from ..agents.question_retrieval import retrieve_question
from ..agents.report_generator import generate_report
from ..agents.resume_analyzer import analyze_resume
from ..agents.rubric_eval_agent import rubric_eval_answer
from .state import QuestionTurn, SessionState
from ..repositories.user_repository import UserRepository
from ..api.database import SessionLocal 

logger = logging.getLogger(__name__)

@contextmanager
def get_db_context():
    """
    Local context manager for database sessions within graph nodes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def analyze_resume_node(state: SessionState) -> dict:
    logger.info("--- Node: Analyzing Resume ---")
    resume_text = state.get("initial_resume_text")
    if not resume_text:
        logger.warning("No resume text found in state.")
        return {"resume_summary": None}
    
    summary = await analyze_resume(resume_text)
    return {"resume_summary": summary.model_dump()}


async def analyze_job_node(state: SessionState) -> dict:
    logger.info("--- Node: Analyzing Job Description ---")
    job_text = state.get("initial_job_description_text")
    if not job_text:
        logger.warning("No job description text found in state.")
        return {"job_summary": None}
    
    summary = await analyze_job_description(job_text)
    return {"job_summary": summary.model_dump()}


# --- THIS FUNCTION IS NOW FIXED ---
async def create_interview_plan_node(state: SessionState) -> dict:
    logger.info("--- Node: Creating Interview Plan ---")
    
    resume_summary_dict = state.get("resume_summary", {})
    job_summary_dict = state.get("job_summary", {})
    personalization_profile = state.get("personalization_profile")

    # This agent call is returning a plain list, not a Pydantic object
    plan_list = await generate_interview_plan(
        resume_summary_dict,
        job_summary_dict,
        personalization_profile
    )
    
    # --- FIX ---
    # The agent returned a list, so we assign it directly.
    # We also store the list as a dict for the context field.
    if not isinstance(plan_list, list):
        logger.error(f"Interview plan agent returned unexpected type: {type(plan_list)}")
        # Handle error, maybe return a default plan
        return {
            "interview_plan": ["behavioral"],
            "interview_plan_context": {"topics": ["behavioral"], "error": "Agent failed"}
        }

    logger.info(f"Generated interview plan: {plan_list}")
    return {
        "interview_plan": plan_list,
        "interview_plan_context": {"topics": plan_list} 
    }
# --- END OF FIX ---


async def question_retrieval_node(state: SessionState) -> dict:
    logger.info("--- Node: Retrieving Question ---")
    plan = state.get("interview_plan", [])
    if not plan:
        logger.warning("Interview plan is empty. Cannot retrieve question.")
        return {"current_question": None}

    current_topic = plan[0]
    
    retrieval_context = {
        "topic": current_topic,
        "resume_summary": state.get("resume_summary"),
        "job_summary": state.get("job_summary"),
        "question_history": state.get("question_history", []),
    }

    question_turn = await retrieve_question(retrieval_context)
    
    return {"current_question": question_turn}


async def deep_dive_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Deep Dive Question ---")
    plan_topic = state.get("interview_plan", [])[0]
    
    question_turn = await generate_deep_dive_question(
        topic_instruction=plan_topic,
        resume_summary=state.get("resume_summary"),
    )
    
    return {"current_question": question_turn}


async def fast_eval_node(state: SessionState) -> dict:
    logger.info("--- Node: Fast Evaluation ---")
    current_question = state.get("current_question")
    if not current_question or not current_question.answer_text:
        logger.warning("No current question or answer to evaluate.")
        return {}

    eval_result = await fast_eval_answer(
        question=current_question.raw_question_text,
        answer=current_question.answer_text,
        ideal_answer=current_question.ideal_answer_snippet
    )
    
    current_question.fast_eval = eval_result.model_dump()
    
    return {"current_question": current_question}


async def rubric_eval_node(state: SessionState) -> dict:
    logger.info("--- Node: Rubric Evaluation ---")
    current_question = state.get("current_question")
    if not current_question or not current_question.answer_text:
        logger.warning("No current question or answer to evaluate.")
        return {}

    eval_result = await rubric_eval_answer(
        question=current_question.raw_question_text,
        answer=current_question.answer_text,
        rubric_id=current_question.rubric_id
    )
    
    current_question.rubric_eval = eval_result.model_dump()
    
    return {"current_question": current_question}


def merge_evaluations_node(state: SessionState) -> dict:
    logger.info("--- Node: Merging Evaluations ---")
    current_question = state.get("current_question")
    if not current_question:
        return {}

    fast_eval = current_question.fast_eval or {}
    rubric_eval = current_question.rubric_eval or {}

    combined_eval = {
        "final_score": rubric_eval.get("aggregate_score", fast_eval.get("score", 0)),
        "feedback_summary": rubric_eval.get("summary", fast_eval.get("quick_summary", "")),
        "details": {
            "fast_eval": fast_eval,
            "rubric_eval": rubric_eval
        },
        "user_input_needed": rubric_eval.get("user_input_needed", False)
    }

    current_question.combined_eval = combined_eval
    
    return {"current_question": current_question}


async def feedback_generation_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Feedback ---")
    current_question = state.get("current_question")
    if not current_question or not current_question.combined_eval:
        logger.warning("No evaluation to generate feedback from.")
        return {}

    feedback_result = await generate_feedback(
        evaluation=current_question.combined_eval,
        question=current_question.raw_question_text,
        answer=current_question.answer_text
    )
    
    current_question.feedback = feedback_result.model_dump()
    
    return {"current_question": current_question}


async def follow_up_node(state: SessionState) -> dict:
    logger.info("--- Node: Checking for Follow-up ---")
    current_question = state.get("current_question")
    if not current_question:
        return {"follow_up_question": None}

    user_input_needed = current_question.combined_eval.get("user_input_needed", False)
    
    if user_input_needed:
        follow_up_result = await generate_follow_up(
            question=current_question.raw_question_text,
            answer=current_question.answer_text,
            evaluation=current_question.combined_eval
        )
        if follow_up_result.follow_up_required:
            logger.info("Follow-up question is required.")
            return {"follow_up_question": follow_up_result.question_text}

    logger.info("No follow-up question needed.")
    return {"follow_up_question": None}


async def report_generator_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Final Report ---")
    
    try:
        serializable_state = dict(state)
        
        if "question_history" in serializable_state and serializable_state["question_history"]:
            serializable_state["question_history"] = [
                turn.model_dump(mode="json") for turn in serializable_state["question_history"]
            ]
        
        if "current_question" in serializable_state and isinstance(serializable_state["current_question"], QuestionTurn):
             serializable_state["current_question"] = serializable_state["current_question"].model_dump(mode="json")

        report_result = await generate_report(serializable_state)
        
        if report_result:
            return {"final_report": report_result.model_dump()}
        else:
            logger.error("Report generation returned None.")
            return {"final_report": None}
            
    except Exception as e:
        logger.error(f"Report generation node failed: {e}", exc_info=True)
        return {"final_report": None}


async def personalization_node(state: SessionState) -> dict:
    logger.info("--- Node: Creating Personalization Plan ---")
    serializable_state = dict(state)
    if state.get("question_history"):
        serializable_state["question_history"] = [
            turn.model_dump(mode="json") for turn in state["question_history"]
        ]
    plan_result = await create_personalization_plan(serializable_state)
    return {"personalization_profile": plan_result.model_dump()}


def final_reporting_entry_node(state: SessionState) -> dict:
    logger.info("--- Node: Kicking off Final Reporting ---")
    return {}


def update_history_and_plan_node(state: SessionState) -> dict:
    logger.info("--- Node: Updating History and Advancing Plan ---")
    last_question = state["current_question"]
    
    # Handle the case where no question was generated (e.g., plan was empty)
    if not last_question:
        logger.warning("update_history_and_plan_node: No current question to add to history.")
        return {
            "interview_plan": state.get("interview_plan", [])[1:], # Still advance the plan
            "current_question": None,
            "follow_up_question": None
        }

    new_history = state.get("question_history", []) + [last_question]
    updated_plan = state.get("interview_plan", [])[1:]
    
    return {
        "question_history": new_history,
        "interview_plan": updated_plan,
        "current_question": None,
        "follow_up_question": None
    }


async def save_personalization_node(state: SessionState) -> dict:
    """
    Saves the personalization_profile to the user's DB record.
    """
    logger = logging.getLogger(__name__)
    logger.info("--- Node: Saving Personalization Profile ---")
    
    profile = state.get("personalization_profile")
    user_id = state.get("user_id")

    if not profile or not user_id:
        logger.warning(
            "No personalization profile or user_id found in state. Skipping save."
        )
        return {}

    try:
        with get_db_context() as db:
            repo = UserRepository(db)
            repo.update_personalization_profile(user_id, profile)
            logger.info(f"Successfully saved profile for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save personalization profile for user {user_id}: {e}")
    
    return {}