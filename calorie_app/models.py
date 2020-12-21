from calorie_app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    calories = db.Column(db.Float)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    foodItems = db.relationship('Food', backref='foodEater', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    perServing = db.Column(db.Integer, nullable=False)
    totalCalorie = db.Column(db.Float, nullable=False)
    totalCarbs = db.Column(db.Float, nullable=False)
    totalFat = db.Column(db.Float, nullable=False)
    totalProtein = db.Column(db.Float, nullable=False)
    eatingDate = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
