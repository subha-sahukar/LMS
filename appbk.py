from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import json
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load user data from JSON file
with open('users.json') as f:
    users = json.load(f)

# Sample chapters for each subject
chapters = {
    "math": [f"Chapter {i}" for i in range(1, 11)],
    "science": [f"Chapter {i}" for i in range(1, 11)],
    "history": [f"Chapter {i}" for i in range(1, 11)],
    "english": [f"Chapter {i}" for i in range(1, 11)]
}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    grade = request.form['grade']
    school = request.form['school']
    
    if username in users and users[username] == password:
        session['username'] = username
        session['grade'] = grade
        session['school'] = school
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('failure'))

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    grade = session.get('grade')
    school = session.get('school')
    subject = request.args.get('subject')
    return render_template('dashboard.html', username=username, grade=grade, school=school, chapters=chapters, subject=subject)

@app.route('/quiz/<subject>/<int:chapter>')
def quiz(subject, chapter):
    username = session.get('username')
    with open(f'quizzes/{subject}_quiz.json') as f:
        questions = random.sample(json.load(f), 5)
    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    return render_template('quiz.html', subject=subject, chapter=chapter, question=questions[0], total_questions=len(questions), current_question=1, username=username)

@app.route('/next_question', methods=['POST'])
def next_question():
    answer = request.form.get('answer')
    current_question = session.get('current_question')
    questions = session.get('questions')
    if answer == questions[current_question]['answer']:
        session['score'] += 1
    session['current_question'] += 1

    if session['current_question'] < len(questions):
        return redirect(url_for('quiz_question'))
    else:
        return redirect(url_for('quiz_result'))

@app.route('/quiz_question')
def quiz_question():
    current_question = session.get('current_question')
    questions = session.get('questions')
    return render_template('quiz.html', question=questions[current_question], total_questions=len(questions), current_question=current_question + 1)

@app.route('/quiz_result')
def quiz_result():
    username = session.get('username')
    subject = request.args.get('subject')
    chapter = request.args.get('chapter')
    score = session.get('score')
    total_questions = len(session.get('questions'))
    percentage = (score / total_questions) * 100
    
    if percentage >= 90:
        rating = 'Excellent'
    elif percentage >= 75:
        rating = 'Good'
    elif percentage >= 50:
        rating = 'Average'
    else:
        rating = 'Needs Improvement'
    
    # Save history
    history_entry = {
        "username": username,
        "subject": subject,
        "chapter": chapter,
        "score": score,
        "total_questions": total_questions,
        "rating": rating,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if not os.path.exists('history'):
        os.makedirs('history')
    
    history_file = 'history/history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(history_entry)
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)
    
    return render_template('result.html', score=score, total_questions=total_questions, rating=rating)

@app.route('/failure')
def failure():
    return render_template('failure.html')

@app.route('/styles.css')
def styles():
    return send_from_directory(os.path.dirname(__file__), 'styles.css')

if __name__ == '__main__':
    app.run(debug=True)
