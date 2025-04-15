from flask import Flask, render_template, url_for, redirect, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import json


app = Flask(__name__)
bcrypt = Bcrypt(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SECRET_KEY'] = 'secret'
app.secret_key = "your_secret_key"  # Required for session management

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            InputRequired(),
            Length(min=4, max=20, message="Username should be between 4 and 20 characters long")
        ],
        render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            Length(min=4, max=20, message="Password should be between 4 and 20 characters long")
        ],
        render_kw={"placeholder": "Password"}
    )
    repeat_password = PasswordField(
        'Repeat Password',
        validators=[
            InputRequired(),
            Length(min=4, max=80, message="Repeat Password should be between 4 and 80 characters long")
        ],
        render_kw={"placeholder": "Repeat Password"}
    )
    email = StringField(
        'Email',
        validators=[
            InputRequired(),
            Length(min=6, max=35, message="Email should be between 6 and 35 characters long")
        ],
        render_kw={"placeholder": "Email"}
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("Username already exists. Please choose a different one.")

    def validate_password(self, password):
        if password.data != self.repeat_password.data:
            raise ValidationError("Passwords do not match. Please try again.")


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            InputRequired(),
            Length(min=4, max=20, message="Username should be between 4 and 20 characters long")
        ],
        render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            Length(min=4, max=20, message="Password should be between 4 and 20 characters long")
        ],
        render_kw={"placeholder": "Password"}
    )
    submit = SubmitField('Login')

# Example list of available movies
available_movies = [
    {"title": "Avengers", "genre": "Action", "duration": "143 min", "format": "2D", "showtimes": ["12:30", "15:00"]},
    {"title": "Barbie", "genre": "Comedy", "duration": "120 min", "format": "2D", "showtimes": ["14:00", "17:30"]},
    {"title": "Oppenheimer", "genre": "Drama", "duration": "180 min", "format": "3D", "showtimes": ["16:00", "19:00"]},
    {"title": "Spider-Man: No Way Home", "genre": "Action", "duration": "148 min", "format": "3D", "showtimes": ["18:00", "20:30"]},
]

users = [
    {"username": "user123", "genres": ["Action", "Comedy"]},
    {"username": "MovieLover", "genres": ["Fantasy", "Action"]},
    {"username": "Cinephile", "genres": ["Comedy", "Drama"]},
]

# Simulate logged-in user
current_user_data = {"username": "current_user", "genres": ["Action", "Comedy"]}

@app.route('/')
def dashboard():
    # Pass available movies to the dashboard
    return render_template('dashboard.html', movies=available_movies)

@app.route('/login', methods=['GET', 'POST'])   
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        print(form.password.data)
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", "danger")
    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/filter-movies', methods=['GET'])
def filter_movies():
    genre = request.args.get('genre', 'all').lower()
    date = request.args.get('date')

    # Load the JSON data
    with open('cinemacity_scraper/cinema_bemowo_movies_today_fromPyCharm.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)

    # Filter movies by genre and date
    filtered_movies = []
    for movie in movies:
        movie_genres = [g.strip().lower() for g in movie['genre'].split(',')]
        if (genre == 'all' or genre in movie_genres) and (not date or movie['date'] == date):
            filtered_movies.append(movie)

    return jsonify({"movies": filtered_movies})

@app.route("/my-movies")
def my_movies():
    # Get favorite movie IDs or titles from the session
    favorite_movie_ids = session.get("favorites", [])
    
    # Safely filter movies by checking if "id" exists or matching on "title"
    favorite_movies = [
        movie for movie in available_movies
        if ("id" in movie and movie["id"] in favorite_movie_ids) or
           ("title" in movie and movie["title"] in favorite_movie_ids)
    ]
    
    return render_template("my_movies.html", favorite_movies=favorite_movies)

@app.route('/toggle-favorite', methods=['POST'])
def toggle_favorite():
    # Toggle a movie's favorite status
    movie_id = request.json.get("movie_id")
    if "favorites" not in session:
        session["favorites"] = []
    favorites = session["favorites"]

    if movie_id in favorites:
        favorites.remove(movie_id)  # Remove from favorites
    else:
        favorites.append(movie_id)  # Add to favorites

    session["favorites"] = favorites
    return jsonify({"success": True, "favorites": favorites})

@app.route('/match')
def match():
    # Find matched users based on shared genres
    matched_users = []
    for user in users:
        shared_genres = set(current_user_data["genres"]) & set(user["genres"])
        if shared_genres:
            matched_users.append({"username": user["username"], "shared_genres": list(shared_genres)})
    return render_template("match.html", matched_users=matched_users)

@app.route("/match-with/<username>")
def match_with(username):
    # Find shared genres with the matched user
    matched_user = next((user for user in users if user["username"] == username), None)
    if not matched_user:
        return redirect(url_for("match"))

    shared_genres = set(current_user_data["genres"]) & set(matched_user["genres"])
    # Filter movies based on shared genres
    suggested_movies = [movie for movie in available_movies if movie["genre"] in shared_genres]
    return render_template("match_suggestions.html", username=username, suggested_movies=suggested_movies)

@app.route("/choose-movie", methods=["POST"])
def choose_movie():
    movie_title = request.json.get("movie_title")
    return jsonify({"message": f"🎉 IT'S A MATCH! You chose {movie_title}."})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





