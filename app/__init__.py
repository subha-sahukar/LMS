from flask import Flask
from app.db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)

with app.app_context():
    # Import parts of our application
    from app import routes, models
    db.create_all()
