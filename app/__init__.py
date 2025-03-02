

#from flask import Flask

#app = Flask(__name__)
#app.config['SECRET_KEY'] = 'your_secret_key'

#from app import routes



from flask import Flask

# Initialize the Flask app
app = Flask(__name__)

# Import the routes defined in this app
import app.routes
