from flask import Flask, render_template, request, redirect, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
  username = request.form['username']
  password = request.form['password']
  # Replace with your authentication logic
  if username == "admin" and password == "password":
    return "Login successful!"
  else:
    return "Invalid credentials, please try again."

# Configure the app for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

# Initialize the database
with app.app_context():
  db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    repeat_password = request.form['repeat_password']
    
    if password != repeat_password:
      return "Passwords do not match, please try again."
    
    # Check if the username already exists
    if User.query.filter_by(username=username).first():
      return "Username already exists, please choose another one."
    
    # Save the new user to the database
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return "Registration successful!"
  
  return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
  username = request.form['username']
  password = request.form['password']
  remember_me = 'remember_me' in request.form
  
  # Authenticate the user
  user = User.query.filter_by(username=username, password=password).first()
  if user:
    session['user_id'] = user.id
    if remember_me:
      session.permanent = True  # Keep the session alive
    return "Login successful!"
  else:
    return "Invalid credentials, please try again."