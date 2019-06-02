from bson.json_util import loads, dumps

from flask import (render_template, session, request,
  redirect, url_for, abort, jsonify, make_response)
from flask_login import login_required, current_user, logout_user

from lightweight import app
from lightweight.mongo import db
from lightweight.project.services.query.article_query import get_article_data
from lightweight.project.services.processor.data_processor import DataProcessor
from lightweight.project.serializers.profile_serializer import initialize_form_data

@app.route('/register', methods=["POST", "GET"])
def register():
  if request.method == 'POST':
    data = {'message': 'Created.', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)
  return render_template('register.html')

@app.route('/login', methods=["POST", "GET"])
def login():
  if request.method == 'POST':
    data = {'message': 'Logged in.', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)
  return render_template('login.html')

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/database', methods=["POST", "GET"])
@login_required
def database():
  if request.method == 'GET':
    return render_template('database.html')
  elif request.method == 'POST':
    query = request.form.to_dict()
    processor = DataProcessor(query=query, db=db)
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
  if request.method == 'POST':
    print('initializing form data...')
    form_data = initialize_form_data(request.form.to_dict())
    return redirect(url_for('dashboard'))
  return render_template('profile.html')

@app.route('/', methods=["GET", "POST"])
@login_required
def dashboard():
  form_data = session['form_data']
  article_data = get_article_data(db, form_data)
  if request.method == 'GET':
    if request.args.get('render') == 'false':
      return jsonify({
        'form_data': form_data,
        'article_data': dumps(article_data),
      })
  return render_template('dashboard.html', form_data=form_data, article_data=article_data)