from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    school = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))

    def __repr__(self):
        return f'<User {self.username}>'

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    chapter = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time_taken = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<History {self.username} - {self.subject} - {self.chapter}>'
