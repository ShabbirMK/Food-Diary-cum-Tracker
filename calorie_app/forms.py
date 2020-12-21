from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from calorie_app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired(), Length(5, 20)],
                           render_kw={"placeholder": "Enter Username"})
    email = StringField('email',
                        validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Enter Email"})

    password = PasswordField('password',
                             validators=[DataRequired(), Length(8, 32)],
                             render_kw={"placeholder": "Enter Password"})

    retypedpassword = PasswordField('retypedpassword',
                                    validators=[
                                        DataRequired(), EqualTo('password')],
                                    render_kw={"placeholder": "Confirm Password"})

    agree = BooleanField('agree')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Enter Username"})
    password = PasswordField('password', validators=[DataRequired()],
                             render_kw={"placeholder": "Enter Password"})
    remember = BooleanField('Remember Me')


class BodyCalorieForm(FlaskForm):
    activities = ['Very Light', 'Light', 'Moderate', 'Heavy', 'Very Heavy']
    heights = [('cms', 'in CMS'), ('inchs', 'in Inchs')]
    weights = [('kgs', 'in KGS'), ('pounds', 'in lbs')]

    age = IntegerField('Age', validators=[DataRequired(), NumberRange(
        min=0, max=100, message="Age must be between 0 and 100")])

    weight = IntegerField('Weight', validators=[DataRequired(
    ), NumberRange(min=0, message="Weight must be non-negative")])

    height = IntegerField('Height', validators=[DataRequired(
    ), NumberRange(min=0, message="Height must be non-negative")])

    gender = RadioField('Gender', default="Male", choices=['Male', 'Female'])

    activity = SelectField('Activity', default="Light",
                           choices=activities, coerce=str)

    weightunits = SelectField('Weight Unit', default="kgs",
                              choices=weights, coerce=str)

    heightunits = SelectField('Activity', default="cms",
                              choices=heights, coerce=str)

    update = BooleanField('Update')

    # submit = SubmitField('Submit')
