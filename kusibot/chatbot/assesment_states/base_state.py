from __future__ import annotations
from abc import ABC, abstractmethod
from kusibot.chatbot.assesment_agent import AssesmentAgent
from kusibot.database.db_repositories import AssessmentRepository, ConversationRepository

class BaseState(ABC):
    """
    Base class for all assessment states.
    """

    @property
    def context(self) -> AssesmentAgent:
        return self._context
    
    @context.setter
    def context(self, context: AssesmentAgent) -> None:
        self._context = context

    @abstractmethod
    def generate_response(self, user_input, conversation_id, assessment_id):
        pass