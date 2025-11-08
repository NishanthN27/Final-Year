# src/interview_system/repositories/question_repository.py
import uuid
from sqlalchemy.orm import Session
from ..models.question import Question
from ..models.review_queue import ReviewQueue


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_from_review_item(
        self, review_item: ReviewQueue, admin_id: uuid.UUID
    ) -> Question:
        """
        Creates a new Question from an approved ReviewQueue item.
        """
        # Extract the structured data from the JSON
        # This structure matches your agent's fallback output
        raw_q_data = review_item.candidate_question_json.get("raw_question", {})

        new_question = Question(
            text=raw_q_data.get("text"),
            domain=raw_q_data.get("domain"),
            difficulty=raw_q_data.get("difficulty"),
            ideal_answer_snippet=raw_q_data.get("ideal_answer_snippet"),
            promoted_by_admin_id=admin_id,
            # The UUID id is auto-generated
        )

        self.db.add(new_question)
        self.db.commit()
        self.db.refresh(new_question)
        return new_question
