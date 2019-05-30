import os
import json
from flask import Flask
from flask import render_template, session, request, redirect, url_for, abort

from flask_wtf.csrf import CSRFProtect

# Initialize app
app = Flask(__name__)

# Protect with CSRF
csrf = CSRFProtect(app)

app.config.update(
  # Set secret key
  SECRET_KEY = os.urandom(32),
  WTF_CSRF_ENABLED = True,
  DEBUG = True,
)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/init', methods=["POST", "GET"])
def initialize():
  data = request.form.to_dict()

  num_locations = int(data['num_locations'])
  print(num_locations)

  def make_location(data, id):
    return {
      'name': data[f'locationName{str(id)}'],
      'latitude': data[f'locationLat{str(id)}'],
      'longitude': data[f'locationLong{str(id)}']
    }

  data['locations'] = [make_location(data, i) for i in range(1, num_locations)]

  form_data = json.dumps(data)
  session['form_data'] = form_data
  return redirect(url_for('dashboard', message=form_data))

@app.route('/dashboard', methods=["GET"])
def dashboard():
  form_data = json.loads(session['form_data'])
  return render_template('dashboard.html',
    form_data=form_data)