from kusibot.chatbot.assesment_states.base_state import BaseState
from kusibot.chatbot.assesment_states.waiting_cat_state import WaitingCategorizationState

class WaitingFreeTextState(BaseState):

    DEFAULT_RESPONSE = "Thanks for sharing. Based on what you described, which of these options best fits how often you've felt that way over the last 2 weeks?\n"

    def generate_response(self, user_input, conversation_id, assessment_id):

        # Get the current question that was asked
        question_json = self.context.get_question_json(assessment_id)

        #Building response
        prompt = self.DEFAULT_RESPONSE
        for i, option in enumerate(question_json['options']):
            prompt += f"\n{i+1}. {option}"
        prompt += "\n\n(Please enter the number)"

        # Changing state of AssesmentAgent to WaitingCategorizationState
        self.context.transition_to_next_state(WaitingCategorizationState())

        # Updating Assesment in DB
        self.context.assess_repo.update_assessment(
            assessment_id,
            current_state=self.context.STATE_WAITING_CATEGORIZATION,
            last_free_text=user_input
        )

        return prompt