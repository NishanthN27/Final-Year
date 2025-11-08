# src/interview_system/models/question.py
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base


class Question(Base):
    __tablename__ = "questions_meta"

    # Use UUID for the primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Store the text, domain, etc.
    text = Column(Text, nullable=False)
    domain = Column(String, index=True, nullable=False)
    difficulty = Column(Integer, nullable=False, default=5)
    ideal_answer_snippet = Column(Text)

    # We will skip this for now, but the column should exist
    rubric_id = Column(String, index=True, nullable=True)

    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    promoted_by_admin_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
