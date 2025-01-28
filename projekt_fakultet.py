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
        {"id": 1, "question": "Które z poniższych miast uznaje się za „miasto kotów”?", "options": ["Ateny", "Warszawa", "Rzym", "Stambuł"], "answer": "Stambuł"},
        {"id": 2, "question": "Jakie jest ulubione danie Garfielda?", "options": ["Pizza", "Warzywa", "Lasagne", "Spaghetti"], "answer": "Lasagne"},
        {"id": 3, "question": "Ile palców ma kot na przednich łapach?", "options": ["3", "4", "5", "6"], "answer": "5"},
        {"id": 4, "question": "Jaki jest największy gatunek kota na świecie?", "options": ["Tygrys syberyjski", "Puma", "Tygrys sumatrzański", "Lew"], "answer": "Tygrys syberyjski"},
        {"id": 5, "question": "Jak nazywa się kot, który ciągle próbuje złapać mysz Jerry'ego w popularnej kreskówce?", "options": ["Garfield", "Sylwester", "Tom", "Simba"], "answer": "Tom"},
        {"id": 6, "question": "Jak nazywa się zły kot, który poluje na smerfy w ich bajce?", "options": ["Klakier", "Azrael", "Tygrys", "Kot z Cheshire"], "answer": "Klakier"},
        {"id": 7, "question": "Która rasa kota jest znana z braku sierści?", "options": ["Maine Coon", "Sfinks", "Syjam", "Ragdoll"], "answer": "Sfinks"},
        {"id": 8, "question": "Jaka jest najmniejsza naturalna rasa kota?", "options": ["Maine Coon", "Syjam", "Kot singapurski", "Devon Rex"], "answer": "Kot singapurski"},
        {"id": 9, "question": "Jaką prędkość może osiągnąć gepard podczas polowania?", "options": ["40 km/h", "60 km/h", "80 km/h", "120 km/h"], "answer": "120 km/h"},
        {"id": 10, "question": "Jak koty odczuwają słodki smak?", "options": ["Bardzo intensywnie", "Podobnie jak ludzie", "Nie potrafią odczuwać smaku słodkiego", "Tylko w małym stopniu"], "answer": "Nie potrafią odczuwać smaku słodkiego"},
        {"id": 11, "question": "Która z ras kotów jest znana z braku ogona?", "options": ["Syjam", "Manx", "Ragdoll", "Sfinks"], "answer": "Manx"},
        {"id": 12, "question": "Dlaczego koty mają pionowe źrenice?", "options": ["Dla lepszej orientacji w przestrzeni", "Aby lepiej widzieć w słabym świetle", "Aby odstraszać wrogów", "Dla ochrony przed słońcem"], "answer": "Aby lepiej widzieć w słabym świetle"},
        {"id": 13, "question": "Które koty jako jedyne żyją w stadach?", "options": ["Tygrysy", "Lwy", "Słonie", "Gepardy"], "answer": "Lwy"},
        {"id": 14, "question": "Jakiego koloru są najczęściej oczy kotów syjamskich?", "options": ["Zielone", "Żółte", "Niebieskie", "Brązowe"], "answer": "Niebieskie"},
        {"id": 15, "question": "Który z tych kotów występuje naturalnie na terenie Polski?", "options": ["Irbis", "Ocelot", "Lew", "Żbik"], "answer": "Żbik"}
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