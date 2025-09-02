# 🧠 KusiBot – AI-Powered Mental Health Chatbot 🤖

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=didierrc_KusiBot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=didierrc_KusiBot)

Welcome to **KusiBot**, an intelligent chatbot designed to assist with **mental health self-assessments**. Using a Multi-Agent System (MAS) architecture and advanced AI models, KusiBot engages in natural conversations to help users reflect on their well-being and identify initial signs of mental health conditions through validated psychological screening tools.

> ⚠️ **Disclaimer:** KusiBot is **not a substitute for professional medical advice**. It is a tool developed for a Final Degree Project and is intended for informational and preliminary assessment purposes only. If you are experiencing a mental health crisis, please contact a qualified professional or a crisis hotline immediately.

---

## 🌟 Features
- 🧠 **Multi-Agent System (MAS) Architecture** – A supervisor agent orchestrates the workflow between specialized agents for intent recognition, general conversation, and assessments.
- 🎭 **Intent Classification** – Uses a fine-tuned **BERT model** to understand user intent (e.g., distinguishing a casual chat from a cry for help).
- 💬 **Empathetic, Private Conversations** – Generates natural, context-aware dialogue using a **locally-run Mistral 7B LLM via Ollama**, ensuring user data remains private and is never sent to third-party servers.
- 📋 **Integrated Mental Health Screening** – Conversationally administers the clinically validated **PHQ-9 (Depression)** and **GAD-7 (Anxiety)** questionnaires.
- 📊 **Professional Monitoring Dashboard** – Includes a secure panel for authorized professionals to review user conversation histories and assessment results.
- 🚀 **Containerized and CI/CD-Ready** – Fully containerized with **Docker** and integrated with **GitHub Actions** for automated testing and code quality analysis.

---

## 🏗️ Tech Stack
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend Language**: Python 3.12
- **Web Framework**: Flask
- **Database**: SQLite with SQLAlchemy ORM
- **AI & ML**:
  - **Intent Classification**: BERT (fine-tuned `bert-base-uncased`) 
  - **LLM Engine**: Mistral 7B running on Ollama (Local LLM) 
  - **Libraries**: Hugging Face Transformers, Langchain, PyTorch
- **Development & CI/CD**: WSL2, Poetry, Pytest, Docker, Gunicorn, GitHub Actions, SonarCloud
- **Model Training Environment**: Google Colab

The fine-tuned BERT model is available on the Hugging Face Hub: [didierrc/MH_BERT](https://huggingface.co/didierrc/MH_BERT)

---

## 🐳 Installation and Setup with Docker

This is the recommended method for running the application in a stable, containerized environment.

### Prerequisites
- Linux environment (WSL2 for Windows' Users)
- [Git](https://git-scm.com/) 
- [Python 3.12+](https://www.python.org/) 
- [Docker](https://www.docker.com/) (Docker Desktop for WSL2)

### 1. Clone the Repository
```bash
git clone [https://github.com/didierrc/KusiBot.git](https://github.com/didierrc/KusiBot.git)
cd KusiBot
```

### 2. Configure the environment variables

- Create a `.env` file from the example template. This file will store your secret keys and professional user credentials.
```bash
cp .env.example .env
```

- Now, open the `.env` file with a text editor and fill in the required variables.
```bash
# Required for session security (generate a random string!)
SECRET_KEY='your_super_secret_key_here'

# Required for Docker containers to locate Ollama service
OLLAMA_BASE_URL=http://ollama:11434

# Credentials for the default professional user account (change me!)
PROFESSIONAL_USERNAME='your_pro_username'
PROFESSIONAL_PASSWORD='your_pro_password'
```

### 3. Navigate to the Deploy Directory
```bash
cd deploy
```

### 4. Build and Start the Services

This command will build the Docker images and start the KusiBot application and the Ollama service in the background.

```bash
docker-compose up -d --build
```

**Note**: The first time you run this, it may take a few minutes to build the images.

### 5. Download Mistral model
The first time the application is executed, it is needed to download the LLM model (the model is cached for next startups).

```bash
docker-compose exec ollama ollama pull mistral
```

### 6. Access the app 
The application is now running in http://localhost:5000.

### 7. Stopping the application
To stop the services and remove the containers, run:

```bash
docker-compose down
```

---

## 🔧 Running Locally (for Development)
This method is recommended for developers who want to contribute to the code.

### Prerequisites
- Linux environment (WSL2 for Windows' Users)
- [Git](https://git-scm.com/) 
- [Python 3.12+](https://www.python.org/) 
- [Docker](https://www.docker.com/) (Docker Desktop for WSL2)
- [Poetry](https://python-poetry.org/) for dependency management
- [Ollama](https://ollama.com/) for running the local LLM and download the Mistral model with:
```bash
ollama pull mistral
```

### 1. Install Dependencies
Poetry will create a virtual environment and install all necessary Python packages.

```bash
poetry install
```

### 2. Activate the Virtual Environment

```bash
poetry env activate
```

### 3. Setup
- Create a `instance` folder in the root of the project for database initialisation.

```bash
mkdir instance
```

- Create a `.env` file from the example template. This file will store your secret keys and professional user credentials.
```bash
cp .env.example .env
```

- Now, open the `.env` file with a text editor and fill in the required variables. There are other variables you can change, check out the example to see their descriptions.
```bash
# Required for session security (generate a random string!)
SECRET_KEY='your_super_secret_key_here'

# Credentials for the default professional user account (change me!)
PROFESSIONAL_USERNAME='your_pro_username'
PROFESSIONAL_PASSWORD='your_pro_password'

# Environment to run KusiBot (dev or testing or prod)
FLASK_ENV='your_environment'
```

### 4. Running KusiBot

```bash
poetry run kusibot
```

Your application will be available at http://localhost:5000

---

## ✅ Running Tests

The project includes a full suite of unit and integration tests. To run them, use Poetry:

```bash
poetry run pytest
```

---

## ✅ KusiBot's Source Code Documentation

The project's documentation is generated using Sphinx and is located in the /docs folder. If you want to add/modify documentation to a new created function/class, add a Python docstring to it.

Once you have documented the new code, you can build the documentation by executing the following command:

```bash
cd docs
poetry run sphinx-build -b html source build/html
```

The output will be generated in the docs/build/html folder. Open index.html in a browser to view the documentation. Any modifications to the source files will require a rebuild to be reflected in the output.

---

## 📜 License & Project Report
This project is open-source and was developed as my Final Degree Project for the Software Engineering Degree at the University of Oviedo. Although I have put my best effort into it, there is always room for enhancements and extensions. Contributions are welcome!

You can read the full project report for a deep dive into the system's analysis, design, and implementation. Feel free to reach out through my email, I don't bite 😉.

---

## 📩 Contact
If you have questions, feedback, or just want to connect, feel free to reach out!

- Author: Didier Yamil Reyes Castro
- Email: didierrc.dev@gmail.com
- GitHub: [didierrc](https://github.com/didierrc) 