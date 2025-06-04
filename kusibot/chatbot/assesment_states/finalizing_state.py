from kusibot.chatbot.assesment_states.base_state import BaseState
from datetime import datetime, timezone
import random

class FinalizingState(BaseState):
    """State for finalizing the assessment after all questions have been answered."""

    RESPONSE_VARIATIONS = [
        "Okay, we've finished with those questions. Thanks so much for sharing all of that with me – it really does take courage to open up. Just a gentle reminder, if things ever feel too heavy, talking things through with a professional can make a real difference.",
        "That's the end of that set of questions. Thanks for taking the time to reflect and answer. Understanding how we're feeling is a really important step. And remember, if you feel you need more support down the line, professionals are there to help.",
        "We made it through all the questions! Thank you for putting in the effort to think about and answer them, I appreciate your honesty. Please keep in mind that reaching out for professional support is always an option if you feel you need it.",
        "Alright, that's all of them! Seriously, thanks for walking through that with me. Talking helps, right? And just so you know, if things ever feel overwhelming, chatting with a professional is always a solid choice.",
        "Finished! Thanks for being open and answering those questions. It's really positive that you're checking in with your feelings. Just wanted to gently add, reaching out to a professional is a strong step to take if you ever feel you need extra support.",
        "Okay, we're done with those questions for now. Thanks for sharing your thoughts. And hey, never hesitate to seek professional help if you feel it could be useful, okay?"
    ]

    def generate_response(self, user_input, conversation_id, assessment_id):

        # Calculating the total score based on the answers
        total_score = self.context.assess_repo.calculate_total_score(assessment_id)
        total_score = total_score if total_score is not None else 0

        print(f"Total score calculated: {total_score}")
        
        # Get total-score interpretation
        assessment = self.context.assess_repo.get_assessment(assessment_id)
        interpretations = self.context.questionnaires[assessment.assessment_type]['interpretations']
    
        interpretation_text = "Not available"
        for interpretation_range, interpretation in interpretations.items():
            # Split the range into lower and upper bounds
            lower, upper = map(int, interpretation_range.split('-'))

            # Check if the score is within the range
            if lower <= total_score <= upper:
                interpretation_text = interpretation
                break
        
        print(f"Interpretation text: {interpretation_text}")

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
        self.context._transition_to_next_state(AskingQuestionState())
        
        # Get the final message
        return random.choice(self.RESPONSE_VARIATIONS)
    