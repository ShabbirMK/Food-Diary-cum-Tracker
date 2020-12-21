from flask import render_template, request, redirect, url_for, session
from flask_login import login_user, current_user, logout_user, login_required

from calorie_app import app, db, CONSUMER_KEY, CONSUMER_SECRET
from werkzeug.security import generate_password_hash, check_password_hash
from calorie_app.forms import RegistrationForm, LoginForm, BodyCalorieForm
from calorie_app.models import User, Food

from fatsecret import Fatsecret
from datetime import datetime

db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for("home"))


@app.route("/login", methods=['GET', 'POST'])
def userlogin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    formLogin = LoginForm()
    formRegister = RegistrationForm()

    if request.method == "GET":
        return render_template('login_register.html',
                               formLogin=formLogin,
                               formRegister=formRegister,
                               register=False)

    else:
        formLogin = LoginForm()
        formRegister = RegistrationForm()

        if "submit_register" in request.form.keys():
            if formRegister.validate_on_submit() and formRegister.agree.data:
                hashed_password = generate_password_hash(
                    formRegister.password.data)

                user = User(username=formRegister.username.data,
                            email=formRegister.email.data,
                            password=hashed_password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for("home"))
            else:
                return render_template('login_register.html',
                                       formLogin=formLogin,
                                       formRegister=formRegister,
                                       register=True)

        else:
            if formLogin.validate_on_submit():

                email = formLogin.email.data
                password = formLogin.password.data

                # Email ID is unique
                user = User.query.filter_by(email=email).first()

                if user and check_password_hash(user.password, password):
                    login_user(user, remember=formLogin.remember.data)
                    return redirect(url_for("home"))

                else:
                    return render_template('login_register.html',
                                           formLogin=formLogin,
                                           formRegister=formRegister,
                                           register=False,
                                           invalid_credentials=True)

            else:
                return render_template('login_register.html',
                                       formLogin=formLogin,
                                       formRegister=formRegister,
                                       register=False)


def record_to_dict(record):
    result = {}
    result['quantity'] = 1
    result['detailsURL'] = record['food_url']
    result['food_name'] = record['food_name']
    result['food_id'] = record['food_id']
    temp = record['food_description'].split("-")
    result['serving_size'] = temp[0]
    temp = list(map(lambda x: x.strip(), temp[1].split("|")))
    for count in temp:
        d = count.split(":")
        result[d[0]] = d[1].strip()

    return result


def totalCalories(allRecords):
    amount = 0
    for _, record in allRecords.items():
        amount += int(record['Calories'].split("k")[0])

    return amount


def calculate_calorie(age, weight, height, gender, activity):
    bmr = 10 * weight + 6.25 * height - 5 * age
    if gender == "Male":
        bmr += 5
    else:
        bmr -= 161

    if activity == "Very Light":
        return round(1.3 * bmr, 1)
    elif activity == "Light":
        return round(1.55 * bmr, 1)
    elif activity == "Moderate":
        return round(1.65 * bmr)
    elif activity == "Heavy":
        return round(1.80 * bmr)
    elif activity == "Very Heavy":
        return round(2.00 * bmr)


@app.route('/body_calorie', methods=['GET', 'POST'])
def body_calorie():
    form = BodyCalorieForm()
    if form.validate_on_submit():
        age = form.age.data
        weight = form.weight.data
        if form.weightunits.data == "pounds":
            weight = weight / 2.2

        height = form.height.data
        if form.heightunits.data == "inchs":
            height = height * 2.54

        gender = form.gender.data
        activity = form.activity.data

        result = calculate_calorie(age, weight, height, gender, activity)

        if current_user.is_authenticated and form.update.data:
            user = User.query.filter_by(email=current_user.email).first()
            user.calories = result
            user.age = age
            user.weight = weight
            user.height = height
            user.gender = gender
            db.session.commit()
            return redirect(url_for('account'))

        else:
            return render_template("body_calorie.html", form=form, result=result)

    return render_template("body_calorie.html", form=form)


def updatedQuantityRecord(record):
    record['Calories'] = round(float(record['Calories'].split("k")[0]), 1) * record['quantity']
    record['Fat'] = round(float(record['Fat'].split("g")[0]), 1) * record['quantity']
    record['Carbs'] = round(float(record['Carbs'].split("g")[0]), 1) * record['quantity']
    record['Protein'] = round(float(record['Protein'].split("g")[0]), 1) * record['quantity']

    return record


@app.route('/food_calorie', methods=['GET', 'POST'])
def food_calorie():
    if request.method == "GET":
        if 'lastSearchedFoodItem' in session.keys():
            return render_template('food_calorie.html',
                                   food=session['lastSearchedFoodItem'],
                                   foodList=enumerate(
                                       session['lastSearchedFoodList']),
                                   diet=enumerate(session['diet'].items()),
                                   summary=totalCalories(session['diet'])
                                   )
        else:
            return render_template('food_calorie.html',
                                   diet=session['diet'])

    elif request.method == "POST":
        # Handling the Search Bar
        if "search" in request.form:
            print(request.form)
            foodItem = request.form.get('fooditem')

            fs = Fatsecret(CONSUMER_KEY, CONSUMER_SECRET)
            foodItems = fs.foods_search(foodItem)
            foodList = []
            for food in foodItems:
                foodList.append(record_to_dict(food))

            session['lastSearchedFoodList'] = foodList
            session['lastSearchedFoodItem'] = foodItem
            session.modified = True

            return render_template('food_calorie.html',
                                   food=foodItem,
                                   foodList=enumerate(foodList),
                                   diet=enumerate(session['diet'].items()),
                                   summary=totalCalories(session['diet'])
                                   )
        # Updation to the Account Page
        else:
            # Here we are by default updating the food entries
            # in terms of each field like Calories and Carbs
            for id, record in session['diet'].items():
                record = updatedQuantityRecord(record)
                foodItem = Food(name=record['food_name'],
                                quantity=record['quantity'],
                                perServing=record['serving_size'],
                                totalCalorie=record['Calories'],
                                totalCarbs=record['Carbs'],
                                totalFat=record["Fat"],
                                totalProtein=record['Protein'],
                                eatingDate=datetime.now(),
                                foodEater=current_user
                                )
                db.session.add(foodItem)
                db.session.commit()

            session['diet'] = {}
            return redirect(url_for('account'))


@app.route('/food_calorie/<int:id>', methods=['POST'])
def add_to_cart(id):
    quantity = max(1, int(request.form.get('quantity')))
    new_record = session['lastSearchedFoodList'][id]
    new_record['quantity'] = quantity

    if new_record['food_id'] in session['diet'].keys():
        session['diet'][new_record['food_id']]['quantity'] += quantity
    else:
        session['diet'][new_record['food_id']] = new_record

    session.modified = True
    return redirect(url_for('food_calorie'))


@app.route('/food_calorie/<name>', methods=['POST'])
def remove_from_cart(name):

    session['diet'][name]['quantity'] -= 1

    if session['diet'][name]['quantity'] == 0:
        del session['diet'][name]

    session.modified = True
    print(session['diet'])
    return redirect(url_for('food_calorie'))


@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))


def generateRecords(records):
    data = {}
    summary = {}
    for record in records:
        if record.eatingDate.strftime("%m/%d/%Y") in data.keys():
            data[record.eatingDate.strftime("%m/%d/%Y")].append(record)
        else:
            data[record.eatingDate.strftime("%m/%d/%Y")] = [record]

    for key, record in data.items():
        data[key] = record[::-1]
        summary[key] = {}
        summary[key]['totalCaloriesOfDay'] = sum([food.totalCalorie for food in record])
        summary[key]['totalFatOfDay'] = sum([food.totalFat for food in record])
        summary[key]['totalProteinOfDay'] = sum([food.totalProtein for food in record])
        summary[key]['totalCarbsOfDay'] = sum([food.totalCarbs for food in record])

    return data, summary


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == "GET":
        # We will send all the food he has eaten
        food = Food.query.filter_by(foodEater=current_user).all()
        # Now we will need to groupby Date
        data, summary = generateRecords(food)
        print(summary)

        return render_template('account.html', foodList=data, summary=summary)
    else:
        # We will send all the food between the mention dates
        fromDate = request.form.get('foodfromdate')
        toDate = request.form.get('foodtodate')

        food = Food.query.filter_by(foodEater=current_user).all()
        sliced = []
        for record in food:
            d = record.eatingDate.strftime("%Y-%m-%d")
            if fromDate < d < toDate:
                sliced.append(record)

        data, summary = generateRecords(food)
        print(summary)
        return render_template('account.html', foodList=data, summary=summary)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')
