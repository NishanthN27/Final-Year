from typing import Literal

from langgraph.graph import END, START, StateGraph

from .nodes import (
    analyze_job_description_node,
    analyze_resume_node,
    create_interview_plan_node,
    deep_dive_question_node,
    evaluation_synthesizer_node,
    fast_eval_node,
    retrieve_question_node,
    rubric_eval_node,
)
from .state import SessionState


def route_to_questioner(
    state: SessionState,
) -> Literal["deep_dive", "retrieve", "__end__"]:
    """
    This router reads the interview plan and decides which question generation
    node to call next.
    """
    if not state.get("interview_plan"):
        print("--- Interview plan complete, ending session ---")
        return END

    next_topic = state["interview_plan"][0]

    if "deep_dive" in next_topic:
        return "deep_dive"
    else:
        return "retrieve"


def route_after_answer(state: SessionState) -> Literal["evaluate", "__end__"]:
    """
    This router checks if the user has provided an answer and directs
    the flow to the evaluation nodes or ends the current turn.
    """
    if state.get("current_question", {}).get("answer_text"):
        return "evaluate"
    return END


# This is our main orchestrator graph
workflow = StateGraph(SessionState)

# Add all the nodes
workflow.add_node("resume_analyzer", analyze_resume_node)
workflow.add_node("job_description_analyzer", analyze_job_description_node)
workflow.add_node("plan_creator", create_interview_plan_node)
workflow.add_node("question_retriever", retrieve_question_node)
workflow.add_node("deep_dive_questioner", deep_dive_question_node)
workflow.add_node("fast_evaluator", fast_eval_node)
workflow.add_node("rubric_evaluator", rubric_eval_node)
workflow.add_node("evaluation_synthesizer", evaluation_synthesizer_node)


# --- Define the graph's structure (the edges) ---

# 1. Start with parallel analysis
workflow.add_edge(START, "resume_analyzer")
workflow.add_edge(START, "job_description_analyzer")

# 2. After analysis, create the interview plan
workflow.add_edge("resume_analyzer", "plan_creator")
workflow.add_edge("job_description_analyzer", "plan_creator")

# 3. After planning, route to the correct question generator
workflow.add_conditional_edges(
    "plan_creator",
    route_to_questioner,
    {
        "deep_dive": "deep_dive_questioner",
        "retrieve": "question_retriever",
        END: END,
    },
)

# 4. After a question is generated, pause for the user's answer
workflow.add_conditional_edges(
    "question_retriever",
    route_after_answer,
    {"evaluate": ["fast_evaluator", "rubric_evaluator"], END: END},
)
workflow.add_conditional_edges(
    "deep_dive_questioner",
    route_after_answer,
    {"evaluate": ["fast_evaluator", "rubric_evaluator"], END: END},
)

# 5. After parallel evaluation, synthesize the results
workflow.add_edge("fast_evaluator", "evaluation_synthesizer")
workflow.add_edge("rubric_evaluator", "evaluation_synthesizer")

# 6. For now, end after synthesis. Later, this will loop back to the question router.
workflow.add_edge("evaluation_synthesizer", END)


# Compile the graph into a runnable app
app = workflow.compile()
