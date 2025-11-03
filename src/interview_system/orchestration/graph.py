# src/interview_system/orchestration/graph.py

import logging
from langgraph.graph import StateGraph, END
from .state import SessionState, QuestionTurn
from .nodes import (
    analyze_job_node,
    analyze_resume_node,
    create_interview_plan_node,
    deep_dive_node,
    fast_eval_node,
    feedback_generation_node,
    final_reporting_entry_node,
    follow_up_node,
    merge_evaluations_node,
    personalization_node,
    question_retrieval_node,
    report_generator_node,
    rubric_eval_node,
    update_history_and_plan_node,
    save_personalization_node
)
# --- WE REMOVED THE BROKEN 'from .routing import ...' LINE ---

logger = logging.getLogger(__name__)

# --- 1. ADD THE MISSING ROUTING FUNCTIONS ---

def route_to_final_reporting(state: SessionState) -> str:
    """
    Router that decides whether to continue the interview or move to final reporting.
    """
    if not state.get("interview_plan"):
        logger.info("--- Router: Interview plan is empty. Ending interview. ---")
        return "end_interview"
    else:
        logger.info("--- Router: Interview plan has items. Continuing. ---")
        return "continue_interview"

def route_to_deep_dive_or_retrieval(state: SessionState) -> str:
    """
    Router that decides whether to retrieve a question or generate a deep dive.
    """
    # This assumes we've just advanced the plan in update_history_and_plan
    # so the *next* question is at plan[0]
    next_topic = state.get("interview_plan", [])[0]
    
    if next_topic.startswith("deep_dive:"):
        logger.info(f"--- Router: Detected 'deep_dive' topic. ---")
        return "deep_dive"
    else:
        logger.info(f"--- Router: Standard topic. Retrieving question. ---")
        return "retrieve_question"

def route_to_follow_up_or_next_question(state: SessionState) -> str:
    """
    Router that decides whether to ask the generated follow-up
    or proceed to the next question.
    """
    if state.get("follow_up_question"):
        logger.info("--- Router: Follow-up question generated. Pausing. ---")
        return "request_follow_up"
    else:
        logger.info("--- Router: No follow-up needed. Proceeding to next question. ---")
        return "proceed_to_next"

# --- END OF NEW FUNCTIONS ---


def get_interview_graph() -> StateGraph:
    """
    Builds the LangGraph state machine for the interview process.
    """
    workflow = StateGraph(SessionState)

    # --- Add all nodes to the graph ---
    workflow.add_node("analyze_resume", analyze_resume_node)
    workflow.add_node("analyze_job", analyze_job_node)
    workflow.add_node("create_interview_plan", create_interview_plan_node)
    workflow.add_node("question_retrieval", question_retrieval_node)
    workflow.add_node("deep_dive_question", deep_dive_node)
    workflow.add_node("fast_eval", fast_eval_node)
    workflow.add_node("rubric_eval", rubric_eval_node)
    workflow.add_node("merge_evaluations", merge_evaluations_node)
    workflow.add_node("feedback_generation", feedback_generation_node)
    workflow.add_node("follow_up_generation", follow_up_node)
    workflow.add_node("update_history_and_plan", update_history_and_plan_node)
    workflow.add_node("final_reporting_entry", final_reporting_entry_node)
    workflow.add_node("report_generator", report_generator_node)
    workflow.add_node("personalization_node", personalization_node)
    workflow.add_node("save_profile", save_personalization_node)
    
    # --- 2. ADD A NEW NODE FOR THE QUESTION ROUTER ---
    # This node just helps visualize the decision point
    workflow.add_node("question_router", lambda x: x)


    # --- Define all edges and routing ---

    # 1. Start: Analyze Resume and Job Description (in parallel)
    workflow.set_entry_point("analyze_resume")
    workflow.add_edge("analyze_resume", "analyze_job")
    
    # 2. After analysis, create the interview plan
    workflow.add_edge("analyze_job", "create_interview_plan")

    # 3. From plan, go to the update node (which acts as the loop start)
    workflow.add_edge("create_interview_plan", "update_history_and_plan")

    # 4. Main interview loop
    workflow.add_conditional_edges(
        "update_history_and_plan",
        route_to_final_reporting,
        {
            "continue_interview": "question_router",
            "end_interview": "final_reporting_entry"
        }
    )

    # 5. Question Router: Decide between RAG or Deep Dive
    workflow.add_conditional_edges(
        "question_router",
        route_to_deep_dive_or_retrieval,
        {
            "retrieve_question": "question_retrieval",
            "deep_dive": "deep_dive_question"
        }
    )
    
    # 6. Evaluation Flow (starts after API gets answer)
    # The API will reinvoke the graph starting at "fast_eval"
    workflow.add_edge("question_retrieval", END) # Pause for user answer
    workflow.add_edge("deep_dive_question", END) # Pause for user answer

    workflow.add_edge("fast_eval", "rubric_eval")
    workflow.add_edge("rubric_eval", "merge_evaluations")
    workflow.add_edge("merge_evaluations", "feedback_generation")
    workflow.add_edge("feedback_generation", "follow_up_generation")

    # 7. Follow-up router
    workflow.add_conditional_edges(
        "follow_up_generation",
        route_to_follow_up_or_next_question,
        {
            "request_follow_up": END, # Pauses for follow-up answer
            "proceed_to_next": "update_history_and_plan" # Loops back
        }
    )

    # 8. Final Reporting (Parallel)
    workflow.add_edge("final_reporting_entry", "personalization_node")
    workflow.add_edge("final_reporting_entry", "report_generator") # 3. Fix typo: was generator_node

    # 9. End States
    workflow.add_edge("report_generator", END) # 3. Fix typo: was generator_node
    
    workflow.add_edge("personalization_node", "save_profile")
    workflow.add_edge("save_profile", END)

    return workflow.compile()

# This part is for visualization, no change needed
if __name__ == "__main__":
    graph = get_interview_graph()
    # You can visualize this graph
    # graph.get_graph().print_ascii()