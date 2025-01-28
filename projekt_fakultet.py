import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_security import Security, UserMixin, RoleMixin, \
    SQLAlchemyUserDatastore, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'developerskie')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'jakas-sol')
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_POST_LOGIN_VIEW'] = '/quiz'

db = SQLAlchemy(app)

roles_user = db.Table(
    'roles_users',
    db.Column('user_id', db.ForeignKey('user.id')),
    db.Column('role_id', db.ForeignKey('role.id')),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_user, backref=db.backref('users'))

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.fs_uniquifier:
            import uuid
            self.fs_uniquifier = str(uuid.uuid4())


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    questions = [
        {"id": 1, "question": "Jaki jest wynik 2+2?", "options": ["3", "4", "5"], "answer": "4"},
        {"id": 2, "question": "Stolica Polski to?", "options": ["Kraków", "Warszawa", "Gdańsk"], "answer": "Warszawa"}
    ]

    if request.method == "POST":
        answers = request.form
        score = 0
        for q in questions:
            if answers.get(str(q["id"])) == q["answer"]:
                score += 1

        new_result = QuizResult(
            user_id=current_user.id,
            score=score,
            timestamp=db.func.now()
        )
        db.session.add(new_result)
        db.session.commit()

        flash(f"Twój wynik to {score}/{len(questions)}", "success")
        return redirect(url_for("leaderboard"))

    return render_template("quiz.html", questions=questions)


@app.route("/results")
@login_required
def results():
    user_results = QuizResult.query.filter_by(user_id=current_user.id).all()
    return render_template("results.html", results=user_results)


@app.route("/leaderboard")
@login_required
def leaderboard():
    top_results = db.session.query(QuizResult, User.email).join(User, QuizResult.user_id == User.id).order_by(QuizResult.score.desc(), QuizResult.timestamp).limit(10).all()
    return render_template("leaderboard.html", leaderboard=top_results)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5001, debug=True)