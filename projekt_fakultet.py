import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_security import Security, UserMixin, RoleMixin, \
    SQLAlchemyUserDatastore, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
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


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.String(255), db.ForeignKey('user.fs_uniquifier'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(128))


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


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route("/")
@login_required
def index():
    filter_by = request.args.get('filter', 'all')
    if filter_by == 'completed':
        tasks = Task.query.filter_by(user_id=current_user.get_id(), completed=True).all()
    elif filter_by == 'not_completed':
        tasks = Task.query.filter_by(user_id=current_user.get_id(), completed=False).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.get_id()).all()
    return render_template("index.html", todo_list=tasks, filter=filter_by)


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
        flash(f"Twój wynik to {score}/{len(questions)}", "success")
        return redirect(url_for("index"))

    return render_template("quiz.html", questions=questions)


@app.route("/add-task", methods=["POST"])
@login_required
def add_task():
    item_text = request.form["item_text"].strip()
    if not item_text:
        flash("Tytuł zadania nie może być pusty.", "error")
        return redirect(url_for("index"))

    new_task = Task(title=item_text, user_id=current_user.get_id())
    db.session.add(new_task)
    db.session.commit()
    flash("Zadanie zostało dodane!", "success")
    return redirect(url_for("index"))


@app.route("/toggle-complete/<int:task_id>")
@login_required
def toggle_complete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.get_id()).first_or_404()
    task.completed = not task.completed
    db.session.commit()
    flash("Status zadania został zmieniony.", "info")
    return redirect(url_for("index"))


@app.route("/delete-task/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.get_id()).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash("Zadanie zostało usunięte.", "warning")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5001, debug=True)
