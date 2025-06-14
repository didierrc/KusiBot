import re, string, torch,json
from transformers import BertTokenizer, BertForSequenceClassification
from threading import Lock

# https://refactoring.guru/es/design-patterns/singleton/python/example#example-1
class IntentRecognizerSingletonMeta(type):
    """
    Singleton metaclass for the IntentRecognizerAgent.
    It is a thread-safe implementation of Singleton.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        
        with cls._lock:
            # If the instance does not exist, create it
            # Otherwise, return the existing instance
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        
        return cls._instances[cls]

class IntentRecognizerAgent(metaclass=IntentRecognizerSingletonMeta):
    """
    BERT-based intent classifier agent.
    This class is responsible for predicting the intent of the user's input.
    """

    BERT_TOKENIZER = "bert-base-uncased"
    CUSTOM_BERT_REPO = "didierrc/MH_BERT"
    TEXT_MAX_LENGTH = 128

    def __init__(self):
        """Initializes the BERT intent classifier model and label mapping."""

        # Whether to use GPU or CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load the trained BERT model and tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(self.BERT_TOKENIZER)
        self.model = BertForSequenceClassification.from_pretrained(self.CUSTOM_BERT_REPO)
        self.model.to(self.device)
        self.model.eval() # Set the model to evaluation mode as we are not training it

        # Creating reverse mapping to get the intent from the class index
        # Try to load label mapping from the Hugging Face repo
        try:
            from huggingface_hub import hf_hub_download
            label_mapping_path = hf_hub_download(
                repo_id=self.CUSTOM_BERT_REPO, 
                filename="label_mapping.json"
            )
            with open(label_mapping_path, 'r') as f:
                self.label_mapping = json.load(f)
        except Exception as e:
            print(f"Error loading label mapping: {e}")
            raise e            

        self.reverse_label_mapping = {class_index: intent for intent, class_index in self.label_mapping.items()}

    def _clean_text(self, text):
        """
        Cleans the input text by removing unwanted characters, links, HTML tags, punctuation, and extra whitespace.
        Also converts the text to lowercase and removes words containing numbers.
        
        Parameters:
            text: The input text to be cleaned.
        Returns:
            str: The cleaned text.
        """
    
        if isinstance(text, str):
            text = text.lower()                                                 # Lowercase statements
            text = re.sub(r'\[[^\]]*\]', '', text)                              # Remove statements in square brackets
            text = re.sub(r'https?://[^\s]+|www\.[^\s]+', '', text)             # Remove links
            text = re.sub(r'<[^>]*>', '', text)                                 # Remove HTML tags
            text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)    # Remove punctuation
            text = text.replace('\n', '')                                       # Remove newlines
            text = re.sub(r'\b\w*\d\w*\b', '', text)                            # Remove words containing numbers
            text = re.sub(r'\s+', ' ', text).strip()                            # Remove extra whitespace

            return text
        return ""
    
    def _get_input_tensors_from_text(self, text):
        """
        Converts the input text into tensors suitable for the BERT model.
        
        Parameters:
            text: The input text to be tokenized.
        Returns:
            tuple: A tuple containing the input IDs and attention mask tensors.
        """

        # Clean the text
        text = self._clean_text(text)

        # Tokenize text
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.TEXT_MAX_LENGTH,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        return encoding['input_ids'].to(self.device), encoding['attention_mask'].to(self.device)

    def predict_intent(self, text):
        """
        Predicts the intent of the input text using the BERT model.
        
        Parameters:
            text: The input text for which the intent needs to be predicted.
            return_confidence: If True, returns the confidence of the prediction.
            
        Returns:
            str: The predicted intent label.
            float: The confidence of the prediction (if return_confidence is True).
        """

        # Get input tensors
        input_ids, attention_mask = self._get_input_tensors_from_text(text)

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
        
        return intent, confidence
