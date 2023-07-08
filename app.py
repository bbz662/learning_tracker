from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(80))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    hours = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            return 'User already exists'

        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return 'Incorrect username or password'

        session['user_id'] = user.id

        return redirect(url_for('activities'))

    return render_template('login.html')

@app.route('/activities', methods=['POST', 'GET'])
def activities():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        hours = request.form.get('hours')

        new_activity = Activity(title=title, description=description, hours=hours, user_id=session['user_id'])
        db.session.add(new_activity)
        db.session.commit()

        return redirect(url_for('activities'))

    activities = Activity.query.filter_by(user_id=session['user_id']).all()

    return render_template('activities.html', activities=activities)

@app.route('/activities/<id>', methods=['POST', 'GET'])
def edit_activity(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    activity = Activity.query.filter_by(id=id, user_id=session['user_id']).first()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        hours = request.form.get('hours')

        activity.title = title
        activity.description = description
        activity.hours = hours
        db.session.commit()

        return redirect(url_for('activities'))

    return render_template('activity_form.html', activity=activity)

@app.route('/activities/delete/<id>')
def delete_activity(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    activity = Activity.query.filter_by(id=id, user_id=session['user_id']).first()

    db.session.delete(activity)
    db.session.commit()

    return redirect(url_for('activities'))

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    activities = Activity.query.filter_by(user_id=session['user_id']).all()

    total_hours = sum([activity.hours for activity in activities])

    return render_template('report.html', activities=activities, total_hours=total_hours)

@app.route('/logout')
def logout():
    session.pop('user_id', None)

    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()  # Create the tables if they don't exist
    app.run(host='0.0.0.0', debug=True)
