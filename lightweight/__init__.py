import os
import pymongo
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

# Configure secret key
SECRET_KEY = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY if SECRET_KEY else os.urandom(32)

# import views
import lightweight.views

# login manager
login_manager = LoginManager()
login_manager.init_app(app)

# load user model
import lightweight.project.services.auth.user

if __name__ == '__main__':
  app.run()