import logging
from typing import Any

# ... (all your agent imports remain the same)
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

logger = logging.getLogger(__name__)


# --- Analysis & Planning Nodes (No Changes) ---
def analyze_resume_node(state: SessionState) -> dict:
    logger.info("--- Node: Analyzing Resume ---")
    resume_text = state.get("initial_resume_text")
    analysis_result = analyze_resume(resume_text)
    return {"resume_summary": analysis_result.model_dump()}

def analyze_job_description_node(state: SessionState) -> dict:
    logger.info("--- Node: Analyzing Job Description ---")
    job_desc_text = state.get("initial_job_description_text")
    analysis_result = analyze_job_description(job_desc_text)
    return {"job_summary": analysis_result.model_dump()}

def create_interview_plan_node(state: SessionState) -> dict:
    logger.info("--- Node: Creating Interview Plan (via Agent) ---")
    resume_summary = state.get("resume_summary")
    job_summary = state.get("job_summary")
    personalization_profile = state.get("personalization_profile")
    plan = generate_interview_plan(
        resume_summary=resume_summary,
        job_summary=job_summary,
        personalization_profile=personalization_profile,
    )
    logger.info(f"Generated Plan: {plan}")
    return {"interview_plan": plan}

def set_current_topic_node(state: SessionState) -> dict:
    plan = state.get("interview_plan", [])
    if plan:
        return {"current_topic": plan[0]}
    return {"current_topic": None}


# --- Question Generation Nodes (No Changes, but added robustness) ---
def introduction_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Introduction ---")
    user_name = "Candidate"
    turn = QuestionTurn(
        conversational_text=f"Welcome, {user_name}! Thanks for your time today. To get started, could you please tell me a bit about yourself and walk me through your resume?",
        raw_question_text="Tell me about yourself.",
        ideal_answer_snippet="A concise 'elevator pitch' summarizing background, key skills, and career goals.",
    )
    return {"current_question": turn}

def retrieve_question_node(state: SessionState) -> dict:
    logger.info("--- Node: Retrieving Generic Question ---")
    topic = state["current_topic"]
    history = state.get("question_history", [])
    last_topics = [turn.raw_question_text for turn in history]
    question_output = retrieve_question(
        domain=topic,
        resume_analysis=state.get("resume_summary"),
        job_analysis=state.get("job_summary"),
        last_topics=last_topics,
    )
    turn = QuestionTurn(
        question_id=question_output.raw_question.question_id,
        conversational_text=question_output.conversational_text,
        raw_question_text=question_output.raw_question.text,
        ideal_answer_snippet=question_output.raw_question.ideal_answer_snippet,
    )
    return {"current_question": turn}

def deep_dive_question_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Deep Dive Question ---")
    topic_string = state["current_topic"]
    parts = topic_string.replace("_", ":").split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid deep_dive format: '{topic_string}'")
    _, item_type, item_name = parts
    
    question_output = generate_deep_dive_question(item_type=item_type, item_name=item_name, resume_summary=state.get("resume_summary"))
    turn = QuestionTurn(
        question_id=None,
        conversational_text=question_output.conversational_text,
        raw_question_text=question_output.raw_question.text,
        ideal_answer_snippet=question_output.raw_question.ideal_answer_snippet,
    )
    return {"current_question": turn}

def wrap_up_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Wrap-up Question ---")
    turn = QuestionTurn(
        conversational_text="That was the last question I had. Do you have any questions for me?",
        raw_question_text="Do you have any questions for me?",
        ideal_answer_snippet="The candidate should ask thoughtful questions about the role, team, or company.",
    )
    return {"current_question": turn}


# --- Evaluation & Synthesis Nodes (No Changes) ---
def fast_eval_node(state: SessionState) -> dict:
    logger.info("--- Node: Fast Evaluation ---")
    current_question = state["current_question"]
    eval_result = fast_eval_answer(question_text=current_question.raw_question_text, ideal_answer_snippet=current_question.ideal_answer_snippet, answer_text=current_question.answer_text)
    return {"current_question": {"evals": {"fast_eval": eval_result.model_dump()}}}

def rubric_eval_node(state: SessionState) -> dict:
    logger.info("--- Node: Rubric Evaluation ---")
    current_question = state["current_question"]
    rubric = state["current_rubric"]
    eval_result = rubric_eval_answer(question_text=current_question.raw_question_text, answer_text=current_question.answer_text, rubric=rubric)
    return {"current_question": {"evals": {"rubric_eval": eval_result.model_dump()}}}

def evaluation_synthesizer_node(state: SessionState) -> dict[str, Any]:
    logger.info("--- Node: Synthesizing Evaluations ---")
    current_question = state["current_question"]
    fast_eval = current_question.evals.get("fast_eval", {})
    rubric_eval = current_question.evals.get("rubric_eval", {})
    fast_score = fast_eval.get("score", 0)
    rubric_score = rubric_eval.get("aggregate_score", 0)
    canonical_score = (rubric_score * 0.7) + (fast_score * 0.3)
    canonical_eval = {"final_score": round(canonical_score, 2), "user_input_needed": rubric_eval.get("user_input_needed", False), "full_rubric": rubric_eval}
    return {"current_question": {"evals": {"canonical": canonical_eval}}}


# --- Feedback & Follow-up Nodes (SIMPLIFIED & CORRECTED) ---
def feedback_generator_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Feedback ---")
    current_question = state["current_question"]
    feedback_result = generate_feedback(question_text=current_question.raw_question_text, answer_text=current_question.answer_text, canonical_evaluation=current_question.evals["canonical"])
    return {"current_question": {"feedback": feedback_result.model_dump()}}

# NEW NAME: follow_up_generator_node to be consistent
def follow_up_generator_node(state: SessionState) -> dict:
    """
    Generates a follow-up question and INSERTS it into the plan.
    This is its ONLY job.
    """
    logger.info("--- Node: Generating and Inserting Follow-up ---")
    current_question = state["current_question"]
    follow_up_agent_output = generate_follow_up(
        question_text=current_question.raw_question_text,
        answer_text=current_question.answer_text,
    )
    
    # Create a new, special follow-up question object
    follow_up_turn = QuestionTurn(
        conversational_text=follow_up_agent_output.question_text,
        raw_question_text=follow_up_agent_output.question_text,
        ideal_answer_snippet="The candidate should provide the specific information missing from their previous answer.",
    )

    # The plan is NOT advanced here. We are just inserting the detour.
    # The state_updater will advance the plan past the original question later.
    return {"follow_up_question": follow_up_turn}


# --- Final Reporting & State Management (SIMPLIFIED & CORRECTED) ---
def report_generator_node(state: SessionState) -> dict:
    logger.info("--- Node: Generating Final Report ---")
    serializable_state = dict(state)
    if state.get("question_history"):
        serializable_state["question_history"] = [turn.model_dump(mode="json") for turn in state["question_history"]]
    report_result = generate_report(serializable_state)
    return {"final_report": report_result.model_dump()}

def personalization_node(state: SessionState) -> dict:
    logger.info("--- Node: Creating Personalization Plan ---")
    serializable_state = dict(state)
    if state.get("question_history"):
        serializable_state["question_history"] = [turn.model_dump(mode="json") for turn in state["question_history"]]
    plan_result = create_personalization_plan(serializable_state)
    return {"personalization_profile": plan_result.model_dump()}

def final_reporting_entry_node(state: SessionState) -> dict:
    logger.info("--- Node: Kicking off Final Reporting ---")
    return {}

def update_history_and_plan_node(state: SessionState) -> dict:
    """
    This node now has ONE job: Archive the last question and advance the plan.
    It is much simpler and safer.
    """
    logger.info("--- Node: Updating History and Plan ---")
    
    # 1. ALWAYS archive the question that was just answered.
    last_question = state["current_question"]
    new_history = state.get("question_history", []) + [last_question]

    # 2. ALWAYS advance the plan. This was the source of the infinite loop.
    updated_plan = state.get("interview_plan", [])[1:]
    
    # 3. Check if a follow-up question was generated in the last step.
    next_question = state.get("follow_up_question") # This comes from follow_up_generator_node

    return {
        "question_history": new_history,
        "interview_plan": updated_plan,
        "current_question": next_question, # This is either the follow-up or None
        "follow_up_question": None, # Clean up the temporary state
    }