# Architecture Documentation: KusiBot

## 1. System Overview

KusiBot is a Mental Health Assessment Chatbot designed to provide a conversational interface for mental health monitoring and assessment. The system follows a Multi-Agent System (MAS) approach, with specialized agents handling different aspects of user interaction. The chatbot differentiates between normal conversation and assessment conversation to create a natural user experience while still collecting clinically relevant data.

## 2. System Architecture

### 2.1 High-Level Component Diagram

```
+--------------------+     +----------------------+
| User Interface     |     | Professional         |
| - Chat Interface   |<--->| Interface            |
| - User Dashboard   |     | - User Management    |
+--------------------+     | - Data Visualization |
         ^                 +----------------------+
         |                           ^
         v                           |
+--------------------+               |
| Dialogue Manager   |               |
| (BERT)             |               |
| - Intent Recog.    |               |
| - Routing Logic    |               |
+--------------------+               |
     ^           ^                   |
     |           |                   |
     v           v                   |
+----------+   +-------------+       |
|Conv.     |   |Assessment   |       |
|Agent     |   |Agent        |       |
|(LLM)     |   |(PHQ-9)      |       |
+----------+   +-------------+       |
     ^           ^                   |
     |           |                   |
     v           v                   |
+----------------------------------+ |
| Conversation Memory              | |
| - User History                   | |
| - Context Management             | |
| - Assessment Results             |-+
+----------------------------------+
```

### 2.2 Data Flow

1. User input is received through the chat interface
2. The Dialogue Manager (BERT) analyzes the input to determine intent
3. Based on the identified intent, the input is routed to either:
   - Conversation Agent for general conversation
   - Assessment Agent for structured mental health assessment
4. The selected agent processes the input and generates a response
5. All interactions are stored in the Conversation Memory
6. Professional users can access and analyze conversation data and assessment results

## 3. Component Details

### 3.1 Dialogue Manager Agent

- **Model**: BERT (Bidirectional Encoder Representations from Transformers)
- **Function**: Intent recognition to determine the user's intent
- **Implementation**:
  - Fine-tuned BERT model with custom intent classes
  - Routes user messages to appropriate agent based on intent classification
  - Handles conversation flow and transitions between agents

### 3.2 Conversation Agent

- **Model**: Large Language Model (options include Deepseek, Mistral AI, Llama, Watsonx, or Ollama)
- **Function**: Engage in normal conversation with users, providing support, empathy, and information
- **Implementation**:
  - Integration with a free LLM model
  - Prompt engineering to guide appropriate responses
  - Context-aware conversation management

### 3.3 Assessment Agent

- **Model**: Questionnaire-driven approach with BERT for categorizing free-text responses
- **Function**: Administer and process standardized mental health questionnaires (PHQ-9 initially)
- **Implementation**:
  - Intent-based questionnaire selection
  - Structured question presentation in conversational format
  - Free-text response handling using BERT categorization
  - Response mapping to standardized options
  - Scoring and interpretation of results

### 3.4 Conversation Memory

- **Function**: Store and manage conversation history and assessment data
- **Implementation**:
  - Database storage of user-chatbot interactions
  - Context retrieval for agent response generation
  - Assessment result storage and tracking
  - Data access for professional review

### 3.5 User Interface

- **Function**: Provide accessible interface for user interaction
- **Implementation**:
  - Web-based chat interface
  - User authentication and profile management
  - Session handling and state management

### 3.6 Professional Interface

- **Function**: Allow mental health professionals to monitor and analyze user interactions
- **Implementation**:
  - Secure authentication with role-based access
  - User management dashboard
  - Conversation review tools
  - Assessment result visualization
  - Flagging system for concerning interactions

## 4. Database Schema - WI`P

### 4.1 Core Entities

- **User**
  - Basic profile information
  - Authentication credentials
  - Conversation history references

- **Message**
  - Content
  - Timestamp
  - Sender type (user/agent)
  - Agent type (conversation/assessment)
  - Intent classification

- **Conversation**
  - User reference
  - Start/end timestamps
  - Summary metrics
  - Flagged status

- **Assessment**
  - User reference
  - Assessment type (PHQ-9, etc.)
  - Question responses with raw text and categorized values
  - Total score
  - Timestamp
  - Interpretation

- **ProfessionalUser**
  - Professional credentials
  - Access controls
  - Assigned users

## 5. Key Processes

### 5.1 Conversation Flow

1. User sends a message
2. BERT model analyzes the message for intent
3. If intent indicates distress or mental health concerns:
   - Assessment Agent is activated
   - PHQ-9 assessment is initiated or continued
4. If intent is conversational:
   - Conversation Agent generates an appropriate response
5. All interactions are stored in Conversation Memory

### 5.2 Assessment Process

1. Assessment Agent receives control from Dialogue Manager
2. PHQ-9 questionnaire is selected based on detected distress indicators
3. Questions are presented conversationally
4. User's free-text responses are:
   - Processed by BERT model
   - Categorized into predefined categories
   - Mapped to standardized questionnaire options
5. After all questions are answered:
   - Score is calculated
   - Preliminary indicator is generated
   - Results are stored
   - Professional is notified if score indicates concern

### 5.3 Professional Monitoring

1. Professional users can log in to monitoring dashboard
2. Dashboard displays:
   - User list with risk indicators
   - Recent assessments and scores
   - Flagged conversations
3. Professionals can review conversation history
4. Assessment results can be exported for clinical documentation

## 6. Technical Implementation

### 6.1 Flask Application Structure

```
kusibot/
├── api/                          # Flask Blueprints
│   ├── auth/                     # Authentication routes
│   ├── chatbot/                  # Chatbot interaction routes
│   ├── frontend/                 # UI static files and templates
│   ├── main/                     # General routes
│   └── professional/             # Professional interface routes
├── chatbot/                      # Chatbot logic
│   ├── intent_recognizer.py      # BERT intent classification
│   ├── dialogue_manager.py       # Routing logic
│   ├── conversation_agent.py     # LLM integration
│   ├── assessment_agent.py       # PHQ-9 implementation
│   ├── memory.py                 # Conversation context storage
│   └── config.py                 # Model configurations
├── database/                     # Database models and connection
│   ├── models.py                 # SQLAlchemy models
│   └── db.py                     # Database initialization
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
└── tests/                        # Test modules
```

### 6.2 API Endpoints

- **/api/auth/**
  - POST /login - User authentication
  - POST /register - User registration
  - GET /logout - User logout

- **/api/chatbot/**
  - POST /message - Submit user message
  - GET /history - Retrieve conversation history
  - GET /assessment/{id} - Get assessment results

- **/api/professional/**
  - GET /users - List all users
  - GET /flagged - List flagged conversations
  - GET /assessments - List all assessments
  - POST /flag/{conversation_id} - Flag a conversation

## 7. Security and Privacy Considerations

- User authentication and authorization
- Encrypted data storage for sensitive information
- De-identification of data for research purposes
- Clear user consent for data collection and storage
- Professional access controls
- Secure API endpoints

## 8. Deployment Architecture

- Containerized deployment using Docker
- CI/CD pipeline via GitHub Actions
- SonarQube code quality scanning
- Scalable infrastructure for production