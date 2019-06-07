import json
from bson.json_util import loads, dumps

from flask import (render_template, session, request,
  redirect, url_for, abort, jsonify, make_response, flash)

from flask_login import login_required, current_user, logout_user, login_user

from flask_cors import cross_origin

from lightweight import app
from lightweight.mongo import db
from lightweight.project.services.query.article_processor import ArticleProcessor
from lightweight.project.services.processor.data_processor import DataProcessor
from lightweight.project.forms.profile_serializer import ProfileSerializer
from lightweight.project.services.auth.user import User
from lightweight.project.forms.login_form import LoginForm
from lightweight.project.forms.register_form import RegisterForm

from werkzeug.security import generate_password_hash

@app.route('/register', methods=["POST", "GET"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))
  form = RegisterForm()
  if request.method == 'POST' and form.validate_on_submit():
    # check if user already exists
    existing_user = db.users.find_one({'_id': form.email.data})
    if existing_user:
      data = {'message': 'User already exists.', 'code': 'ERROR'}
      return render_template('register.html', form=form, data=data)
    user_data = {
      '_id': form.email.data,
      'email': form.email.data,
      'password': generate_password_hash(form.password.data)
    }
    user_id = db.users.insert_one(user_data).inserted_id
    if user_id:
      user_obj = User(user_id)
      login_user(user_obj)
      return redirect(url_for('profile'))
  return render_template('register.html', form=form)

@app.route('/login', methods=["POST", "GET"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))
  form = LoginForm()
  if request.method == 'POST' and form.validate_on_submit():
    user = db.users.find_one({'_id': form.email.data})
    if user and User.validate_login(user['password'], form.password.data):
      user_obj = User(user['_id'])
      login_user(user_obj)
      return redirect(url_for('dashboard'))
    data = {'message': 'Wrong username or password.', 'code': 'ERROR'}
    return render_template('login.html', form=form, data=data)
  else:
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/profile', methods=["GET", "POST", "PUT"])
@login_required
def profile():
  profile = current_user.profile
  profile_obj = json.loads(dumps(profile))
  errors = []
  if request.method != 'GET':
    serializer = ProfileSerializer(current_user)
    if request.method == 'POST':
      if not profile:
        data = serializer.parse(request)
        db.profiles.insert_one(data)
        response = jsonify({'message': 'Successfully created profile', 'status': 200, 'response_type': 'application/json'})
        return response
      errors.append('Profile already exists.')
      response = jsonify({'errors': errors, 'status': 400, 'response_type': 'application/json'})
      return response

    if request.method == 'PUT':
      data = serializer.parse(request)
      print('data:', data)
      db.profiles.replace_one({'_id': current_user.email}, data)
      response = jsonify({'message': 'Successfully updated profile', 'status': 200, 'response_type': 'application/json'})
      return response
  return render_template('profile.html', profile_obj=profile_obj)

@app.route('/database', methods=["POST", "GET"])
@login_required
def database():
  if request.method == 'GET':
    return render_template('database.html')
  elif request.method == 'POST':
    query = request.form.to_dict()
    processor = DataProcessor(query=query, db=db)
    return redirect(url_for('dashboard'))

@app.route('/', methods=["GET", "POST"])
@login_required
def dashboard():
  profile = current_user.profile
  profile_obj = json.loads(dumps(profile))
  if not profile:
    return redirect(url_for('profile'))
  # article_data = json.loads(dumps(get_article_data(db, profile)))
  if request.method == 'GET':
    return render_template('dashboard.html', profile_obj=profile_obj)