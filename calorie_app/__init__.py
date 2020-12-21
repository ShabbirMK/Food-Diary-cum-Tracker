from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'userlogin'
login_manager.login_message_category = 'info'

CONSUMER_KEY = '53b9a3d128794a0aaf7cd65c7d7be05b'
CONSUMER_SECRET = 'ea7f407f5e0c40ac9f4b9635a8ba013e'

from calorie_app import routes
