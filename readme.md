## QED42-task-Query-Recommender
## Overview

This project simulates a **GenAI-powered recommendion system** that generates recommended queries based on a user's browsing history or session on a website. The system tracks user sessions, captures page metadata and user interactions, and generates relevant query suggestions to enhance user engagement. 

For the purposes of this assignment, we have created a **mock website** named **"CodeBuddy 2.0"**, which is designed to demonstrate how user interactions, session data, and recommendations work in a real-world scenario.

Codebuddy 2.0 learning platform, which is a platform focused on learning programming, offers courses on programming, software testing, data structures, algorithms, and other topics, resources and articles through categories and blogs.

## Tools and Models

- **Frontend**: HTML, CSS, JavaScript (for page interactions and UI elements)
- **Backend**: Python with Flask (for session tracking and query generation)
- **Session Tracking**: Custom JavaScript class to track and log user interactions
- **Query Generation**: Llama3 8b LLM model throgh groq.
- **Database**:Sqlite3 (for storing user's browsing history)
- **RAG**: Langchain,Llama3 8b LLM,FAISS,HuggingFaceEmbeddings

## Folder Structure

#### Application Files

- app.py: Primary Flask application file containing routes and core logic
- rag.py: Implementation of Retrieval Augmented Generation system
- predefined_metadata.py: page for predefined topics metadata 

#### Database Files

- tracking.db: SQLite database storing user session data and interactions
- vectorstore/db_faiss/: FAISS vector store for efficient similarity search
- index.faiss: Binary index file for vector storage
- index.pkl: Pickled metadata associated with vectors


#### Static Assets

- static/images/: Contains all website images
- static/scripts/: JavaScript files for client-side functionality
- static/css/: Stylesheet files for website styling

#### Templates
templates/: Contains HTML templates for different pages

- Core pages: index.html, login.html
- Course pages: dsa-guide.html, fullstack.html, java.html
- Other pages: blog.html, questions.html

## System Requirements

- Python 3.11 or higher
- pip (Python package installer)
- Git
- Code Editor(eg. VS code)

## Setup Instructions
Follow these steps to set up the project on your local machine:

### Step 1: Clone the Repository

First, clone the repository containing the CodeBuddy 2.0 project to your local machine:

```bash
git clone https://github.com/omkardev7/QED42-task-Query-Recommender.git
```
### Step 2: Navigate to the Project Directory
```bash
cd QED42-task-Query-Recommender
```
### Step 3: Set Up Python Virtual Environment
```bash
python3 -m venv venv
```
Activate the virtual environment:
```bash
venv\Scripts\activate
```

### Step 4: Install Python Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configuration
1. Environment Setup
- Create .env file:
- Add configuration:
```bash
GROQ_API_KEY=your_groq_secret_key
SECRET_KEY=your_secret_key_here
```
2. Vector Store Setup
- create folders vectorstore/db_faiss or
 ```bash
# Create directories
mkdir -p vectorstore/db_faiss
```
### Step 6: Run the Application
This will start a development server, and you can open the website in your browser at:
 ```bash
http://127.0.0.1:5000/
```
