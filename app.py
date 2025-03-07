from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load user data from JSON file
with open('users.json') as f:
    users = json.load(f)

# Load subjects and chapters from JSON file
with open('subjects.json') as f:
    subjects = json.load(f)

# Load subtopics and their content from JSON file
with open('subtopics.json') as f:
    subtopics_content = json.load(f)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    grade = request.form.get('grade')
    school = request.form.get('school')

    if username in users and users[username] == password:
        session['username'] = username
        session['grade'] = grade
        session['school'] = school
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('failure'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    grade = session['grade']
    school = session['school']
    grade_subjects = subjects.get(grade, {})
    return render_template('dashboard.html', username=username, grade=grade, school=school, subjects=grade_subjects)

@app.route('/get_topics/<grade>/<subject>')
def get_topics(grade, subject):
    topics = subjects.get(grade, {}).get(subject, [])
    return jsonify({'topics': topics})

@app.route('/chapter/<grade>/<subject>/<chapter>')
def chapter(grade, subject, chapter):
    if 'username' not in session:
        return redirect(url_for('home'))

    subtopics = list(subtopics_content.get(grade, {}).get(subject, {}).get(chapter, {}).keys())
    username = session['username']
    history_file = f'history/{username}_history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    chapter_history = [entry for entry in history if entry['grade'] == grade and entry['subject'] == subject and entry['chapter'] == chapter]
    
    return render_template('chapter.html', grade=grade, subject=subject, chapter=chapter, subtopics=subtopics, history=chapter_history)

@app.route('/quiz/<grade>/<subject>/<chapter>')
def quiz(grade, subject, chapter):
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    chapter_number = chapter.split()[-1]
    quiz_file = f'quizzes/{grade}/{subject}/Grade{grade[-1]}_{subject}_chapter{chapter_number}.json'
    try:
        with open(quiz_file) as f:
            questions = json.load(f)
    except FileNotFoundError:
        return f"Quiz file {quiz_file} not found", 404

    sample_size = min(len(questions), 10)
    questions = random.sample(list(questions), sample_size)
    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    session['incorrect'] = []
    session['start_time'] = datetime.utcnow()
    return render_template('quiz_content.html', grade=grade, subject=subject, chapter=chapter, question=questions[0], total_questions=len(questions), current_question=1, username=username, time_limit=10)

@app.route('/next_question', methods=['POST'])
def next_question():
    if 'username' not in session:
        return redirect(url_for('home'))

    answer = request.form.get('answer')
    current_question = session['current_question']
    questions = session['questions']

    if isinstance(answer, list):
        correct_answers = set(questions[current_question]['answer'])
        given_answers = set(answer)
        if correct_answers == given_answers:
            session['score'] += 1
        else:
            session['incorrect'].append({
                'question': questions[current_question]['question'],
                'given_answer': ', '.join(given_answers),
                'correct_answer': ', '.join(correct_answers)
            })
    else:
        if answer == questions[current_question]['answer']:
            session['score'] += 1
        else:
            session['incorrect'].append({
                'question': questions[current_question]['question'],
                'given_answer': answer,
                'correct_answer': questions[current_question]['answer']
            })

    session['current_question'] += 1

    if session['current_question'] < len(questions):
        return redirect(url_for('quiz_question', grade=request.form.get('grade'), subject=request.form.get('subject'), chapter=request.form.get('chapter')))
    else:
        return redirect(url_for('quiz_result', grade=request.form.get('grade'), subject=request.form.get('subject'), chapter=request.form.get('chapter')))

@app.route('/quiz_question')
def quiz_question():
    if 'username' not in session:
        return redirect(url_for('home'))

    current_question = session['current_question']
    questions = session['questions']
    grade = request.args.get('grade')
    subject = request.args.get('subject')
    chapter = request.args.get('chapter')
    return render_template('quiz_content.html', question=questions[current_question], total_questions=len(questions), current_question=current_question + 1, grade=grade, subject=subject, chapter=chapter, time_limit=10)

@app.route('/quiz_result')
def quiz_result():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    grade = request.args.get('grade')
    subject = request.args.get('subject')
    chapter = request.args.get('chapter')
    score = session['score']
    total_questions = len(session['questions'])
    incorrect = session['incorrect']
    percentage = (score / total_questions) * 100

    # Calculate time taken
    start_time = session['start_time']
    end_time = datetime.utcnow()
    time_taken = end_time - start_time
    minutes, seconds = divmod(time_taken.total_seconds(), 60)
    time_taken_str = f"{int(minutes)} minutes and {int(seconds)} seconds"

    if percentage >= 90:
        rating = 'Excellent'
    elif percentage >= 75:
        rating = 'Good'
    elif percentage >= 50:
        rating = 'Average'
    else:
        rating = 'Needs Improvement'

    # Convert UTC to IST
    ist_time = end_time + timedelta(hours=5, minutes=30)
    history_entry = {
        "username": username,
        "grade": grade,
        "subject": subject,
        "chapter": chapter,
        "score": score,
        "total_questions": total_questions,
        "rating": rating,
        "date": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
        "time_taken": time_taken_str
    }

    # Save history locally (example implementation, adjust as necessary)
    if not os.path.exists('history'):
        os.makedirs('history')
    history_file = f'history/{username}_history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    history.append(history_entry)
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)

    return render_template('result.html', score=score, total_questions=total_questions, rating=rating, time_taken=time_taken_str, username=username, grade=grade, subject=subject, chapter=chapter, incorrect=incorrect)

@app.route('/revise/<grade>/<subject>/<chapter>')
def revise(grade, subject, chapter):
    if 'username' not in session:
        return redirect(url_for('home'))

    content = get_revise_content(subject, chapter)
    return render_template('revise.html', grade=grade, subject=subject, chapter=chapter, content=content)

def get_revise_content(subject, chapter):
    # This function should be updated to fetch the correct content based on subject and chapter.
    # For now, we return a static summary for the example provided.
    if subject == "Science" and chapter == "Animal Habitat":
        return "Adaptations in living beings: The presence of specific body features and certain habits which enable a plant or an animal to live in a particular habitat is called adaptation."
    return "Content not available."

@app.route('/revise/<grade>/<subject>/<chapter>/<subtopic>')
def revise_subtopic(grade, subject, chapter, subtopic):
    if 'username' not in session:
        return redirect(url_for('home'))

    content = subtopics_content.get(grade, {}).get(subject, {}).get(chapter, {}).get(subtopic, [])
    content_type = 'bullet_points' if isinstance(content, list) else 'flash_cards'
    return render_template('subtopic.html', grade=grade, subject=subject, chapter=chapter, subtopic=subtopic, content=content, content_type=content_type)

@app.route('/abort_quiz', methods=['POST'])
def abort_quiz():
    if 'username' not in session:
        return redirect(url_for('home'))

    return redirect(url_for('dashboard'))

@app.route('/failure')
def failure():
    return render_template('failure.html')

@app.route('/styles.css')
def styles():
    return send_from_directory(app.static_folder, 'styles.css')

@app.route('/history/<grade>/<subject>/<chapter>')
def history(grade, subject, chapter):
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    history_file = f'history/{username}_history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    chapter_history = [entry for entry in history if entry['grade'] == grade and entry['subject'] == subject and entry['chapter'] == chapter]
    return render_template('history.html', history=chapter_history)

@app.route('/edit_profile')
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    user = users.get(username, {})
    return render_template('edit_profile.html', username=username, first_name=user.get('first_name', ''), last_name=user.get('last_name', ''), grade=session.get('grade'), school=session.get('school'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    users[username]['first_name'] = first_name
    users[username]['last_name'] = last_name

    # Save updated user data to JSON file
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

    return redirect(url_for('dashboard'))

@app.route('/reset_password')
def reset_password():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    return render_template('reset_password.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
