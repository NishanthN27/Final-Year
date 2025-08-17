# scripts/test_full_graph_flow.py

import os
import uuid
from dotenv import load_dotenv

# This setup is necessary to run the script standalone
import sys
import pathlib
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import the uncompiled workflow, not the pre-compiled app
from interview_system.orchestration.graph import workflow
from interview_system.orchestration.state import SessionState, QuestionTurn

# A simple in-memory checkpointer for testing
from langgraph.checkpoint.memory import MemorySaver

def main():
    """
    Runs a full end-to-end test of the graph, including submitting an answer.
    """
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in .env file.")
        return

    # Use an in-memory checkpointer for this test run
    memory = MemorySaver()
    # Compile the graph here with the checkpointer
    graph_with_checkpointing = workflow.compile(checkpointer=memory)

    print("--- Testing Full Graph Flow ---")

    # 1. Define the initial state of the interview
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    initial_state: SessionState = {
        "session_id": session_id,
        "user_id": user_id,
        "initial_resume_text": "Experienced Python developer with 5 years in backend systems.",
        "initial_job_description_text": "Seeking a senior Python engineer for a role in distributed systems.",
        "question_history": [],
        # The rest of the state starts empty
        "resume_summary": None,
        "job_summary": None,
        "current_question": None,
        "personalization_profile": None,
    }

    # This config tells LangGraph which conversation thread to use
    config = {"configurable": {"thread_id": str(session_id)}}

    # 2. Run the graph from the beginning
    print("\n--- Invoking graph: Initial analysis and question retrieval ---")
    final_state = None
    for chunk in graph_with_checkpointing.stream(initial_state, config=config):
        print(f"Node: {list(chunk.keys())[0]}")
        final_state = list(chunk.values())[0]

    print("\n--- Graph finished first run ---")
    if final_state and final_state.get("current_question"):
        current_question = final_state["current_question"]
        print(f"Question Retrieved: {current_question.question_text}")

        # 3. Simulate the user providing an answer
        print("\n--- Simulating user answer ---")
        user_answer = "To design a URL shortener, I would use a distributed key-value store and a hashing algorithm to generate unique IDs."
        
        # Manually update the state with the answer
        current_question.answer_text = user_answer
        
        # We need to update the state in the checkpointer
        graph_with_checkpointing.update_state(
            config,
            {"current_question": current_question}
        )

        # 4. Resume the graph to run the evaluation
        # We pass `None` as the input because the state is already saved
        print("\n--- Resuming graph for evaluation ---")
        eval_final_state = None
        # This part of the graph is not yet built, but this is how you would call it
        # for chunk in graph_with_checkpointing.stream(None, config=config):
        #     print(f"Node: {list(chunk.keys())[0]}")
        #     eval_final_state = list(chunk.values())[0]
        
        print("\n(Placeholder for evaluation nodes - flow will be added to graph.py)")

    else:
        print("Error: Graph did not produce a question.")


if __name__ == "__main__":
    main()
