from kusibot.chatbot.assesment_states.base_state import BaseState
from kusibot.chatbot.assesment_states.waiting_free_state import WaitingFreeTextState

class AskingQuestionState(BaseState):

    def generate_response(self, user_input, conversation_id, assessment_id):
        
        # Get the next question to ask
        question_json = self.context.get_question_json(assessment_id)

        # Get the model natural lead-in phrase
        lead_in = self.context.naturalize_question(question_json['question'],
                                                   question_json['id'],
                                                   assessment_id.user_id)
        
        # Changing state of AssesmentAgent to WaitingFreeTextState
        self.context.transition_to_next_state(WaitingFreeTextState())

        # Updating state Assesment in DB
        self.context.assess_repo.update_assessment(
            assessment_id,
            current_state=self.context.STATE_WAITING_FREE_TEXT
        )
        
        return lead_in
