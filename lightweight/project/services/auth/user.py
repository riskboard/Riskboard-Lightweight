
from flask import redirect, url_for, jsonify
from werkzeug.security import check_password_hash
from lightweight import login_manager
from lightweight.mongo import db

class User():
  def __init__(self, email):
    self.email = email

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return self.email

  @property
  def profile(self):
    return db.profiles.find_one({'_id': self.email})

  @staticmethod
  def validate_login(password_hash, password):
    return check_password_hash(password_hash, password)

@login_manager.user_loader
def load_user(email):
  u = db.users.find_one({"_id": email})
  if not u:
      return None
  return User(u['_id'])

@login_manager.unauthorized_handler
def unauthorized():
  return redirect(url_for('login'))