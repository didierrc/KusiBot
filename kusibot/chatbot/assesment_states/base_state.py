from __future__ import annotations
from abc import ABC, abstractmethod

class BaseState(ABC):
    """
    Base class for all assessment states.
    """

    @property
    def context(self):
        return self._context
    
    @context.setter
    def context(self, context):
        self._context = context

    @abstractmethod
    def generate_response(self, user_input, conversation_id, assessment_id):
        pass