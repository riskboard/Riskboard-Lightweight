import os
import pymongo
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect
from flask_cors import CORS

app = Flask(__name__)

# Configure secret key
SECRET_KEY = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY if SECRET_KEY else os.urandom(32)

# CSRF Protect
csrf = CsrfProtect(app)

# CORS
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# login manager
login_manager = LoginManager()
login_manager.init_app(app)

# import views
import lightweight.views

# load user model
import lightweight.project.services.auth.user

if __name__ == '__main__':
  app.run()