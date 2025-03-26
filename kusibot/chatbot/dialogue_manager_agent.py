import re, string, torch,json
from transformers import BertTokenizer, BertForSequenceClassification

BERT_TOKENIZER = "bert-base-uncased"
CUSTOM_BERT_REPO = "didierrc/MH_BERT"
TEXT_MAX_LENGTH = 128

class DialogueManagerAgent:
    """
    BERT-based intent classifier for the chatbot. 
    This class is responsible for predicting the intent of the user's input.
    """

    def __init__(self, label_mapping_path=None):
        """Initializes the BERT intent classifier model and label mapping."""

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(BERT_TOKENIZER)
        
        # Load the trained BERT model
        self.model = BertForSequenceClassification.from_pretrained(CUSTOM_BERT_REPO)
        self.model.to(self.device)
        self.model.eval() # Set the model to evaluation mode as we are not training it

        # Creating reverse mapping to get the intent from the class index
        if label_mapping_path:
            with open(label_mapping_path, 'r') as f:
                self.label_mapping = json.load(f)
        else:
            # Try to load label mapping from the Hugging Face repo
            try:
                from huggingface_hub import hf_hub_download
                label_mapping_path = hf_hub_download(
                    repo_id=CUSTOM_BERT_REPO, 
                    filename="label_mapping.json"
                )
                with open(label_mapping_path, 'r') as f:
                    self.label_mapping = json.load(f)
            except Exception as e:
                print(f"Error loading label mapping: {e}")
                raise e            

        self.reverse_label_mapping = {class_index: intent 
                                              for intent, class_index in self.label_mapping.items()}

    def clean_text(self, text):
        """Cleans user's text by removing special characters, spaces, etc."""

        if isinstance(text, str):
            text = text.lower()                                                 # Lowercase statements
            text = re.sub(r'\[.*?\]', '', text)                                 # Remove statements in square brackets
            text = re.sub(r'https?://\S+|www\.\S+', '', text)                   # Remove links
            text = re.sub(r'<.*?>+', '', text)                                  # Remove HTML tags
            text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)    # Remove punctuation
            text = re.sub(r'\n', '', text)                                      # Remove newlines
            text = re.sub(r'\w*\d\w*', '', text)                                # Remove words containing numbers
            text = re.sub(r'\s+', ' ', text).strip()                            # Remove extra whitespace

            return text
        return ""
    
    def get_input_tensors_from_text(self, text):
        """Tokenizes the text and returns the input tensors for the model."""

        # Clean the text
        text = self.clean_text(text)

        # Tokenize text
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=TEXT_MAX_LENGTH,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        return encoding['input_ids'].to(self.device), encoding['attention_mask'].to(self.device)

    def predict_intent(self, text, return_confidence=False):
        """Predicts the intent of the user's text input."""

        # Get input tensors
        input_ids, attention_mask = self.get_input_tensors_from_text(text)

        # Get prediction
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        
        # Get the predicted index class
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=1)
        confidence, predicted_class = torch.max(probs, dim=1)
        
        # Convert to numpy for easier handling
        predicted_class = predicted_class.cpu().numpy()[0]
        confidence = confidence.cpu().numpy()[0]
        
        # Get the intent label
        intent = self.reverse_label_mapping[predicted_class]
        
        if return_confidence:
            return intent, confidence
        return intent
