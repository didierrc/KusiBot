from kusibot.chatbot.assesment_states.base_state import BaseState
from kusibot.chatbot.assesment_states.waiting_cat_state import WaitingCategorizationState
import random

class WaitingFreeTextState(BaseState):

    RESPONSE_VARIATIONS = [
        "Got it, thanks for telling me. Based on what you described, which of these options best fits how often you've felt that way over the last 2 weeks?",
        "Okay, I hear you. Thinking about what you've mentioned, could you select the option that best describes the frequency over the last 2 weeks?",
        "Right, thanks for explaining that. To help map that feeling, which option here matches your experience most closely over the last 2 weeks?",
        "Okay, I really appreciate you sharing that. Looking at these choices, which one best reflects how often this occurred for you over the last 2 weeks?",
        "Right, that gives me a better picture. Now, considering the frequency over the last 2 weeks, please choose the option below that applies best.",
    ]

    def generate_response(self, user_input, conversation_id, assessment_id):

        # Get the current question that was asked
        question_json = self.context.get_question_json(assessment_id)

        #Building response
        prompt = f"{random.choice(self.RESPONSE_VARIATIONS)}\n"
        for i, option in enumerate(question_json['options']):
            prompt += f"\n{i+1}. {option}"
        prompt += "\n\n(Just pop the number in)"

        # Changing state of AssesmentAgent to WaitingCategorizationState
        self.context.transition_to_next_state(WaitingCategorizationState())

        # Updating Assesment in DB
        self.context.assess_repo.update_assessment(
            assessment_id,
            current_state=self.context.STATE_WAITING_CATEGORIZATION,
            last_free_text=user_input
        )

        return prompt