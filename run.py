from flask import Flask
from app import app as application

# Initialize the Flask app with the static folder set to 'static'
application = Flask(__name__, static_folder='static')

# Import the routes defined in the app
import app.routes

if __name__ == '__main__':
    application.run(debug=True)
