from kusibot.chatbot.assesment_states.base_state import BaseState
from datetime import datetime, timezone

class FinalizingState(BaseState):

    DEFAULT_RESPONSE_MSG = "Thanks for answering all the questions, speaking about your feelings is important. Remember that you can always reach out to a professional if you need help."

    def generate_response(self, user_input, conversation_id, assessment_id):

        # Calculating the total score based on the answers
        total_score = self.context.assess_repo.calculate_total_score(assessment_id)
        total_score = total_score if total_score is not None else 0
        
        # Get total-score interpretation
        interpretations = self.context.get_question_json(assessment_id)["interpretation"]
        interpretation_text = "Not available"
        for interpretation_range, interpretation in interpretations.items():
            # Split the range into lower and upper bounds
            lower, upper = map(int, interpretation_range.split('-'))

            # Check if the score is within the range
            if lower <= total_score <= upper:
                interpretation_text = interpretation
                break

        # Closing the assessment
        self.context.assess_repo.update_assessment(
                        assessment_id,
                        end_time=datetime.now(timezone.utc),
                        total_score=total_score,
                        interpretation=interpretation_text,
                        current_state=self.context.STATE_FINISHED,
                        last_free_text=None
                    )
        
        # Returning assesment object to the initial state
        # In case another assessment is started
        from kusibot.chatbot.assesment_states.asking_question_state import AskingQuestionState
        self.context.transition_to_next_state(AskingQuestionState())
        
        # Get the final message
        return self.DEFAULT_RESPONSE_MSG
    