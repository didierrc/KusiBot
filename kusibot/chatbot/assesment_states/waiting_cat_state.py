from kusibot.chatbot.assesment_states.base_state import BaseState
from kusibot.chatbot.assesment_states.finalizing_state import FinalizingState
from kusibot.chatbot.assesment_states.asking_question_state import AskingQuestionState

class WaitingCategorizationState(BaseState):

    ERROR_NUMBER_RESPONSE = "Sorry, I need the number corresponding to the option. Can you please provide the number?"

    def generate_response(self, user_input, conversation_id, assessment_id):
        
        # Get the current question that was asked
        question_json = self.context.get_question_json(assessment_id)
        
        try:
            selected_index = int(user_input.strip()) - 1
            
            if 0 <= selected_index < len(question_json['options']):
                
                # Get the current assessment
                assessment = self.context.assess_repo.get_assessment(assessment_id)
                
                # Save question result
                self.context.assess_question_repo.save_assessment_question(
                    assessment_id=assessment_id,
                    question_number=assessment.current_question,
                    question_text=question_json['text'],
                    user_response=user_input,
                    categorized_value=selected_index
                )
                        
                # Check if assessment is complete
                total_questions = len(self.context.questionnaires[assessment.assessment_type]['questions'])
                if assessment.current_question + 1 > total_questions: # All questions answered
                    
                    # Changing state and triggering finalization
                    self.context.transition_to_next_state(FinalizingState())
                    return self.context.state.generate_response(
                        user_input,
                        conversation_id,
                        assessment_id
                    )
                
                else: # More questions to answer
                    
                    # Changing state
                    self.context.transition_to_next_state(AskingQuestionState())

                    # Updating assesment in DB
                    self.context.assess_repo.update_assessment(
                        assessment_id,
                        current_state=self.context.STATE_ASKING,
                        current_question=assessment.current_question + 1,
                        last_free_text=None
                    )
                    
                    # Return next question
                    return self.context.state.generate_response(
                        user_input,
                        conversation_id,
                        assessment_id
                    )
                 
            else: # Selected index is out of range
                return self.ERROR_NUMBER_RESPONSE
        
        except ValueError: # Input not a number
            return self.ERROR_NUMBER_RESPONSE

        