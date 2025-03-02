

#from flask import Flask

#app = Flask(__name__)
#app.config['SECRET_KEY'] = 'your_secret_key'

#from app import routes


from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
