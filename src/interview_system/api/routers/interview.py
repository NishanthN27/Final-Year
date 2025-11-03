# src/interview_system/api/routers/interview.py

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ...schemas.session import (
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from ...services.pdf_parser import extract_text_from_pdf_url
from ...orchestration.graph import get_interview_graph
from ...orchestration.state import SessionState
from ...auth.dependencies import get_current_user
from ...repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# --- ADD THE PREFIX AND TAGS ---
# This works with main.py to create the /api/interview path
router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)
# --- END OF FIX ---


@router.post(
    "/sessions",
    response_model=StartInterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new interview session",
)
async def create_new_interview_session(
    request: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Starts a new interview session.
    This endpoint parses the resume, creates an initial state,
    and invokes the graph to get the first question.
    """
    logger.info("--- Endpoint: Creating New Interview Session ---")
    user_id_str = current_user.get("user_id")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user credentials",
        )
    
    user_id = uuid.UUID(user_id_str)

    # 1. Get Resume Text
    resume_text = ""
    if request.file_url:
        try:
            resume_text = await extract_text_from_pdf_url(str(request.file_url))
            logger.info(f"Successfully parsed PDF for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to parse PDF from URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse PDF from the provided URL.",
            )
    elif request.resume_text:
        resume_text = request.resume_text
    else:
        logger.warning(f"No resume provided for new session by user {user_id}")
        # We can proceed without a resume, the agent will handle it

    # 2. --- THIS IS THE PERSONALIZATION LOGIC ---
    # Fetch the user's *previous* personalization profile
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    previous_profile = user.personalization_profile if user else None
    if previous_profile:
        logger.info(f"Loaded previous personalization profile for user {user_id}")
    else:
        logger.info(f"No previous profile found for user {user_id}. Starting fresh.")
    # --- END NEW LOGIC ---

    # 3. Create the initial state for the graph
    initial_state = SessionState(
        session_id=uuid.uuid4(),
        user_id=user_id,
        initial_resume_text=resume_text,
        initial_job_description_text=request.job_description,
        
        # Inject the loaded profile
        personalization_profile=previous_profile,
        
        # Initialize all other fields
        resume_summary=None,
        job_summary=None,
        interview_plan=[],
        interview_plan_context=None,
        question_history=[],
        current_question=None,
        follow_up_question=None,
        final_report=None,
    )

    # 4. Invoke the graph to get the first question
    try:
        graph = get_interview_graph()
        # This runs analyze_resume, analyze_job, create_interview_plan, etc.
        final_state = await graph.ainvoke(initial_state) 
        
        first_question = final_state.get("current_question")

        if not first_question:
            logger.error("Graph finished without generating a first question.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate the first interview question.",
            )

        # TODO: Persist the initial session state to your 'sessions' table here
        
        return StartInterviewResponse(
            session_id=str(final_state["session_id"]),
            first_question=first_question.conversational_text,
        )

    except Exception as e:
        logger.error(f"Error during initial graph invocation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while starting the interview.",
        )


@router.post(
    "/sessions/{session_id}/answer",
    response_model=SubmitAnswerResponse,
    summary="Submit an answer to the current question",
)
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submits the candidate's answer to the current question and
    runs the evaluation and feedback loop.
    """
    logger.info(f"--- Endpoint: Submitting Answer for Session {session_id} ---")
    
    # TODO: Retrieve the session's current state from your 'sessions' table
    # For now, this logic is incomplete as it depends on session persistence
    
    # This is a conceptual example. You would load the state.
    # current_state = load_session_state(session_id, db)
    
    # current_state["current_question"].answer_text = request.answer_text
    
    # graph = get_interview_graph()
    
    # final_state = await graph.ainvoke(current_state, config={"callable": "fast_eval"})

    # This is a placeholder response
    return SubmitAnswerResponse(
        feedback="Your answer has been received.",
        next_question="This is a placeholder for the next question.",
    )