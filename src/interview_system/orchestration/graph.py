from typing import List, Literal

from langgraph.graph import END, START, StateGraph

from .nodes import (
    analyze_job_description_node, analyze_resume_node, create_interview_plan_node,
    deep_dive_question_node, evaluation_synthesizer_node, fast_eval_node,
    feedback_generator_node, final_reporting_entry_node, follow_up_generator_node, # Renamed
    introduction_node, personalization_node, report_generator_node,
    retrieve_question_node, rubric_eval_node, set_current_topic_node,
    update_history_and_plan_node, wrap_up_node
)
from .state import SessionState


def route_to_questioner(state: SessionState) -> str:
    # If the state_updater just prepared a follow-up, ask it immediately.
    if state.get("current_question"):
        return "pause_for_answer"

    topic = state.get("current_topic")
    if not topic or not state.get("interview_plan"):
        return "generate_report_and_plan"
    if topic == "introduction":
        return "introduction"
    if "deep_dive" in topic:
        return "deep_dive"
    if topic == "wrap_up":
        return "wrap_up"
    return "retrieve"


def route_after_question_is_answered(state: SessionState) -> str:
    # This router is now simpler. It only checks if an answer exists.
    if state.get("current_question") and state["current_question"].answer_text:
        return "run_evaluation"
    else:
        # This will be hit by the "pause_for_answer" node.
        return END


def route_after_evaluation(state: SessionState) -> str:
    canonical_eval = state["current_question"].evals.get("canonical", {})
    if canonical_eval.get("user_input_needed", False):
        return "generate_follow_up" # Route to the generator
    else:
        return "generate_feedback"


workflow = StateGraph(SessionState)

# Add Nodes
workflow.add_node("resume_analyzer", analyze_resume_node)
workflow.add_node("job_description_analyzer", analyze_job_description_node)
workflow.add_node("plan_creator", create_interview_plan_node)
workflow.add_node("topic_setter", set_current_topic_node)
workflow.add_node("introduction_questioner", introduction_node)
workflow.add_node("question_retriever", retrieve_question_node)
workflow.add_node("deep_dive_questioner", deep_dive_question_node)
workflow.add_node("wrap_up_questioner", wrap_up_node)
workflow.add_node("run_evaluation", lambda state: {}) # Passthrough for parallel eval
workflow.add_node("fast_evaluator", fast_eval_node)
workflow.add_node("rubric_evaluator", rubric_eval_node)
workflow.add_node("evaluation_synthesizer", evaluation_synthesizer_node)
workflow.add_node("generate_feedback", feedback_generator_node)
workflow.add_node("generate_follow_up", follow_up_generator_node) # Renamed
workflow.add_node("state_updater", update_history_and_plan_node)
workflow.add_node("final_reporting_entry", final_reporting_entry_node)
workflow.add_node("report_generator", report_generator_node)
workflow.add_node("personalization_planner", personalization_node)
# This is a simple passthrough node that will connect to the pausing router.
workflow.add_node("pause_for_answer", lambda state: {})

# --- Define Edges ---

# 1. Planning
workflow.add_edge(START, "resume_analyzer")
workflow.add_edge(START, "job_description_analyzer")
workflow.add_edge("resume_analyzer", "plan_creator")
workflow.add_edge("job_description_analyzer", "plan_creator")
workflow.add_edge("plan_creator", "topic_setter")

# 2. Routing from Topic Setter
workflow.add_conditional_edges("topic_setter", route_to_questioner, {
    "introduction": "introduction_questioner",
    "deep_dive": "deep_dive_questioner",
    "retrieve": "question_retriever",
    "wrap_up": "wrap_up_questioner",
    "pause_for_answer": "pause_for_answer", # If a follow-up is ready, just pause.
    "generate_report_and_plan": "final_reporting_entry",
})

# 3. Pausing Logic
for node in ["introduction_questioner", "question_retriever", "deep_dive_questioner", "wrap_up_questioner", "pause_for_answer"]:
    workflow.add_conditional_edges(node, route_after_question_is_answered)

# 4. Evaluation Path
workflow.add_edge("run_evaluation", "fast_evaluator")
workflow.add_edge("run_evaluation", "rubric_evaluator")
workflow.add_edge("fast_evaluator", "evaluation_synthesizer")
workflow.add_edge("rubric_evaluator", "evaluation_synthesizer")

# 5. Post-Evaluation Routing
workflow.add_conditional_edges("evaluation_synthesizer", route_after_evaluation, {
    "generate_feedback": "generate_feedback",
    "generate_follow_up": "generate_follow_up",
})

# 6. THE MAIN LOOP: Both feedback and follow-up now lead to the state updater.
workflow.add_edge("generate_feedback", "state_updater")
workflow.add_edge("generate_follow_up", "state_updater")
workflow.add_edge("state_updater", "topic_setter")

# 7. Final Reporting
workflow.add_edge("final_reporting_entry", "report_generator")
workflow.add_edge("final_reporting_entry", "personalization_planner")
workflow.add_edge("report_generator", END)
workflow.add_edge("personalization_planner", END)

app = workflow.compile()