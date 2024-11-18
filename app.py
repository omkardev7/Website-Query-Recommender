import time
from datetime import datetime
import sqlite3
from flask import Flask, render_template, jsonify, request, session, g
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Predefined page metadata
page_metadata = {
    "index": {"topics": ["Introduction to CodeBuddy 2.0", "Features of CodeBuddy 2.0", "Courses Offered on CodeBuddy 2.0","Refund Policies and Incentives"], "importance": 1},
    "blog": {"topics": ["AI", "blockchain", "development"], "importance": 3},
    "courses": {"topics": ["blockchain", "DSA", "java", "software testing"], "importance": 5},
    "dsa-guide": {"topics": ["stack", "array", "python"], "importance": 4},
    "fullstack": {"topics": ["react", "node.js", "mongodb", "express", "native"], "importance": 4},
    "java": {"topics": ["java backend development"], "importance": 2},
    "soft_test": {"topics": ["manual testing", "unit testing", "performance testing"], "importance": 3}
}

# Initialize SQLite database for tracking
DATABASE = 'tracking.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize database schema
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS user_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                page TEXT NOT NULL,
                topics TEXT,
                time_spent INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        ''')
        db.commit()

# Helper function to get topics for a page
def get_page_topics(page):
    page_data = page_metadata.get(page, {})
    topics = page_data.get('topics', [])
    return ','.join(topics) if topics else ''

# API endpoint to track user interactions
@app.route('/track_interaction', methods=['POST'])
def track_interaction():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        session_id = session.get('session_id')
        if not session_id:
            session_id = f"sess-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            session['session_id'] = session_id

        page = data.get('page', '')
        topics = get_page_topics(page)  # Get predefined topics for the page

        db = get_db()
        
        # Update existing record or create new one
        cursor = db.execute('''
            SELECT id, clicks, time_spent 
            FROM user_tracking 
            WHERE session_id = ? AND page = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (session_id, page))
        
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Update existing record
            db.execute('''
                UPDATE user_tracking 
                SET clicks = clicks + ?, time_spent = time_spent + ?
                WHERE id = ?
            ''', (data.get('clicks', 0), data.get('timeSpent', 0), existing_record['id']))
        else:
            # Create new record with predefined topics
            db.execute('''
                INSERT INTO user_tracking (session_id, page, topics, clicks, time_spent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                page,
                topics,  # Using predefined topics
                data.get('clicks', 0),
                data.get('timeSpent', 0),
                datetime.utcnow().isoformat()
            ))
        
        db.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes for pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/dsa-guide')
def dsa_guide():
    return render_template('dsa-guide.html')

@app.route('/fullstack')
def fullstack():
    return render_template('fullstack.html')

@app.route('/java')
def java():
    return render_template('java.html')

@app.route('/soft_test')
def soft_test():
    return render_template('soft_test.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/questions')
def questions():
    return render_template('questions.html')

# Route to generate session context
def generate_session_context():
    try:
        session_id = session.get('session_id')
        if not session_id:
            return []

        db = get_db()
        cursor = db.execute('''
            SELECT page, topics, 
                   COALESCE(time_spent, 0) as time_spent, 
                   COALESCE(clicks, 0) as clicks
            FROM user_tracking
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', (session_id,))
        
        data = cursor.fetchall()
        if not data:
            return []

        # Build session context using predefined metadata and actual behavior
        context = []
        for row in data:
            if row and row['page']:
                # Get predefined importance
                base_importance = page_metadata.get(row['page'], {}).get('importance', 1)
                # Calculate interaction score (normalized)
                interaction_score = (row['time_spent'] * 0.7 + row['clicks'] * 0.3) / 100
                # Combine predefined importance with actual interaction
                total_importance = base_importance * (1 + interaction_score)
                
                context.append({
                    "page": row['page'],
                    "topics": row['topics'].split(',') if row['topics'] else [],
                    "importance": total_importance
                })
        
        return context
    except Exception as e:
        print(f"Error generating context: {str(e)}")
        return []

# Prepare input text for LLaMA3 model
def prepare_input_for_llama(context):
    if not context:
        return "No user browsing history available. Please generate 5 general queries."
    
    context_text = "User's browsing session context:\n"
    for page in context:
        context_text += f"Page: {page['page']}\n"
        context_text += f"Topics: {', '.join(page['topics'])}\n"
        context_text += f"Importance Score: {page['importance']:.2f}\n\n"
    context_text += "Based on the above user's interests and topics, generate 5 diverse specific queries one by one without reasoning."
    print(context_text)
    return context_text

# Function to interact with the GROQ API for generating queries
def generate_queries_using_groq(input_text):
    if not groq_api_key:
        return ["Error: GROQ API key not configured."]

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": input_text}],
        "max_tokens": 200,
        "temperature": 0.2,
        "top_p": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        return ["Error: Invalid API response format"]
    except requests.exceptions.RequestException as e:
        print(f"API request error: {str(e)}")
        return ["Error: Failed to generate queries."]
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return ["Error: Something went wrong."]

# Route to generate dynamic queries
@app.route('/generate_queries', methods=['GET'])
def generate_dynamic_queries():
    try:
        context = generate_session_context()
        input_text = prepare_input_for_llama(context)
        queries = generate_queries_using_groq(input_text)
        
        if isinstance(queries, str):
            # Split string into list, filter out empty lines
            query_list = [q.strip() for q in queries.split('\n') if q.strip()]
            return jsonify({"queries": query_list})
        return jsonify({"queries": queries})
    except Exception as e:
        return jsonify({"error": str(e), "queries": ["Error generating queries."]}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)