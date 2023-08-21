import re

from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_session import Session
from werkzeug.security import check_password_hash
from helpers import calculate_daily_water_intake, check_user_by_id, check_user_by_username, get_article_by_id, get_articles, get_latest_bodyfat_and_bodymass, get_latest_user_water_intake, get_total_articles, get_total_workouts, get_workouts, login_required, calculate_healthy_weight_range, get_distinct_user_activity_data, get_age_and_gender, get_latest_user_activity, get_latest_weight_and_height, register_user, register_user_change_password, validate_confirmation_password, validate_contact_inputs, validate_email, validate_existing_email, validate_password, validate_username
from helpers import calculate_bmi_and_category, calculate_healthy_weight_range, create_weight_plot, create_bmi_plot, calculate_weight_difference, get_all_user_activity, get_all_user_activity_by_registered_at_desc

from activity_validations import validate_activity_type, validate_age, validate_body_fat_percentage, validate_duration, validate_exercise_heart_rate, validate_gender, validate_height, validate_intensity, validate_muscle_mass, validate_resting_heart_rate, validate_water_intake, validate_weight

app = Flask(__name__)

# Number of articles to display per page
ARTICLES_PER_PAGE = 6

# Number of workouts to display per page
WORKOUTS_PER_PAGE = 8

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///healthcare.db")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Get login form input data
        username_or_email = request.form.get("username").lower()
        password = request.form.get("password")

        # List to store error messages
        messages = []

        # Ensure username was submitted
        if not username_or_email:
            messages.append(("danger", "Username or email is required"))

        # Ensure password was submitted
        elif not password:
            messages.append(("danger", "Password is required"))

        if not messages:
            # Check if the username or emails exist in database
            user_row = db.execute("SELECT id, username, hashed_password FROM users WHERE username = :user_or_email OR email = :user_or_email LIMIT 1", user_or_email=username_or_email)

            # Check if the query returned a valid user and valid password
            if len(user_row) != 1 or not check_password_hash(user_row[0]["hashed_password"], password):
                messages.append(("danger", "Invalid username, email, and/or password"))

        if messages:
            # Flash the error messages
            for error in messages:
                flash(error)
            return render_template("login.html", messages=messages, username_or_email=username_or_email)

        # Remember which user has logged in
        session["user_id"] = user_row[0]["id"]
        session["user_username"] = user_row[0]["username"]

        # Check if the "Remember Me" checkbox is checked
        remember_me = request.form.get("remember")

        # Set the permanent session cookie to True if "Remember Me" is checked
        if remember_me:
            session.permanent = True

        # Redirect user to the home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get the register form input data
        username = request.form.get("username").lower()
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # List to store error messages
        messages = []

        # Check if username already exists
        existing_username_rows = check_user_by_username(db, username)

        if existing_username_rows:
            messages.append(("danger", "Username already taken."))

        # Username validation
        validate_username(username, messages)

        # Check if email already exists
        validate_existing_email(db, email, messages)

        # Email validation
        validate_email(email, messages)

        # Password validation
        validate_password(password, messages)

        # Confirmation password validation
        validate_confirmation_password(password, confirmation, messages)

        if messages:
            # Flash the error messages
            for error in messages:
                flash(error)
            return render_template("register.html", messages=messages, username=username, email=email)
        else:
            # Insert the new user into the database
            new_user_rows = register_user(db, username, email, password)

            if not new_user_rows:
                messages.append(("danger", "An error occurred while creating your account. Please try again."))
            else:
                # Get the newly registered user's ID
                new_user_db = db.execute("SELECT id, username FROM users WHERE username = ?", username)[0]

                if new_user_db:
                    # Store the ID of the newly registered user in the session for automatic login
                    session["user_id"] = new_user_db["id"]
                    session["user_username"] = new_user_db["username"]

                    messages.append(("success", "Account successfully created."))

                    flash(messages[-1])

                    # Redirect the user to the home page
                    return redirect("/")

    else:
        return render_template("register.html")

@app.route("/account")
@login_required
def account():
    # Get the logged-in user from the session
    user_id = session.get("user_id")

    user_db = check_user_by_id(db, user_id)

    if not user_db:
        return flash("danger", "User not found")

    return render_template('account.html', user=user_db[0])

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Get the change password form input data
    user_id = session.get("user_id")

    # List to store error messages
    messages = []

    if not user_id:
        messages.append(("danger", "User not found."))

    if request.method == 'POST':
        # Handle the password change form submission
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirmation = request.form.get('confirmation')

        # Check if the current password was provided
        if not current_password:
            messages.append(("danger", "Current password is required."))
        else:
            # Check if user id exists in the database
            user_db = check_user_by_id(db, user_id)

            if not user_db:
                messages.append(("danger", "User not found."))
            elif not check_password_hash(user_db[0]["hashed_password"], current_password):
                messages.append(("danger", "Current password is incorrect."))
            else:
                # Check if new password and confirmation are valid
                if not new_password:
                    messages.append(("danger", "New Password is required."))
                else:
                    validate_password(new_password, messages)
                    if new_password == current_password:
                        messages.append(("danger", "New password must be different from the current password."))

                # Ensure the new password and confirmation match
                validate_confirmation_password(new_password, confirmation, messages)

                if not messages:
                    result_db = register_user_change_password(db, new_password, user_id)

                    if not result_db:
                        messages.append(("danger", "An error occurred while changing your password. Please try again."))
                    else:
                        messages.append(("success", "Password successfully changed."))

                        # Flash the success message
                        flash(messages[-1])

                        # Redirect the user to the home page
                        return redirect("/")

    # Flash the error messages
    for error in messages:
        flash(error)

    return render_template('change_password.html')

@app.route('/workouts')
def workouts():
    page = int(request.args.get('page', 1))
    selected_category = request.args.get('category')

    # Get workouts from the database based on the selected category
    workouts = get_workouts(db, selected_category, page, WORKOUTS_PER_PAGE)

    # Get the total number of workouts
    total_workouts = get_total_workouts(db, selected_category)
    # Calculate the total number of pages
    total_pages = (total_workouts + WORKOUTS_PER_PAGE - 1) // WORKOUTS_PER_PAGE

    # Get all distinct workout categories from the database
    all_categories = db.execute("SELECT DISTINCT category FROM workouts")

    # Convert the categories to a list of strings
    categories = [category['category'] for category in all_categories]

    # Convert workouts to a list of dictionaries
    workout_data = []
    for workout in workouts:
        workout_data.append({
            'name': workout['name'],
            'description': workout['description'],
            'image_path': workout['image_path'],
            'category': workout['category']
        })

    return render_template('workouts.html', workout_data=workout_data, categories=categories, pagination=page, total_pages=total_pages, total_workouts=total_workouts)

@app.route('/articles')
def articles():
    # Get the page number from the URL query parameters
    page = request.args.get('page', 1, type=int)

    # Get articles from the database, ordered by created_at in descending order, and paginate the results
    articles = get_articles(db, page, ARTICLES_PER_PAGE)

    # Get the total number of articles in the database
    total_articles = get_total_articles(db)

    return render_template('articles.html', articles=articles, pagination=page, total_articles=total_articles, ARTICLES_PER_PAGE=ARTICLES_PER_PAGE)

@app.route('/article/<int:article_id>')
def show_article(article_id):
    article = get_article_by_id(db, article_id)

    if not article:
        flash("danger", "Article not found")
        return render_template('article_details.html')
    else:
        # Split the content column into paragraphs
        paragraphs = article['content'].split('|')

        # Convert the created_at attribute to a datetime object
        created_at = article['created_at'][:10]

        return render_template('article_details.html', article=article, paragraphs=paragraphs, created_at=created_at)

@app.route('/activity', methods=['GET', 'POST'])
@login_required
def activity():
    # Get the logged-in user from the session
    user_id = session.get("user_id")

    # List to store error messages
    messages = []

    if not user_id:
        messages.append(("danger", "User not found."))

    if request.method == 'POST':
        # Get the activity form inputs
        age = request.form.get('age')
        gender = request.form.get('gender')
        weight = request.form.get('weight')
        height = request.form.get('height')
        activity_type = request.form.get('activityType')
        duration = request.form.get('duration')
        intensity = request.form.get('intensity')
        resting_heart_rate = request.form.get('restingHeartRate')
        exercise_heart_rate = request.form.get('exerciseHeartRate')
        body_fat_percentage = request.form.get('bodyFatPercentage')
        muscle_mass = request.form.get('muscleMass')
        water_intake = request.form.get('waterIntake')

        # Input validations
        if not age:
            messages.append(("danger", "Age is required."))
        else:
            age, messages = validate_age(age, messages)

        validate_gender(gender, messages)

        if not weight:
            messages.append(("danger", "Weight is required."))
        else:
            weight, messages = validate_weight(weight, messages)

        if not height:
            messages.append(("danger", "Height is required."))
        else:
            height, messages = validate_height(height, messages)

        validate_activity_type(activity_type, messages)

        if not duration:
            messages.append(("danger", "Duration is required."))
        else:
            duration, messages = validate_duration(duration, messages)

        validate_intensity(intensity, messages)

        if not resting_heart_rate:
            messages.append(("danger", "Resting Heart Rate is required."))
        else:
            resting_heart_rate, messages = validate_resting_heart_rate(resting_heart_rate, messages)

        if not exercise_heart_rate:
            messages.append(("danger", "Exercise Heart Rate is required."))
        else:
            exercise_heart_rate, messages = validate_exercise_heart_rate(exercise_heart_rate, messages)

        if not body_fat_percentage:
            messages.append(("danger", "Body Fat Percentage is required."))
        else:
            body_fat_percentage, messages = validate_body_fat_percentage(body_fat_percentage, messages)

        if not muscle_mass:
            messages.append(("danger", "Muscle Mass is required."))
        else:
            muscle_mass, messages = validate_muscle_mass(muscle_mass, messages)

        if not water_intake:
            messages.append(("danger", "Water Intake is required."))
        else:
            water_intake, messages = validate_water_intake(water_intake, messages)

        if not messages:
            # Create a new activity with the form data
            added_activity = db.execute("INSERT INTO activities (user_id, age, gender, weight, height, activity_type, duration, intensity, resting_heart_rate, exercise_heart_rate, body_fat_percentage, muscle_mass, water_intake, registered_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                       user_id, age, gender, weight, height, activity_type, duration, intensity, resting_heart_rate, exercise_heart_rate, body_fat_percentage, muscle_mass, water_intake)

            if not added_activity:
                messages.append(("danger", "An error occurred while adding the activity. Please try again."))
            else:
                messages.append(("success", "Activity successfully added."))

                flash(messages[-1])

                # Redirect to the /stats route
                return redirect(url_for('stats'))
        else:
            # Flash the error messages
            for error in messages:
                flash(error)
            return render_template('user_activity.html', messages=messages, age=age, gender=gender, weight=weight, height=height, activity_type=activity_type, duration=duration, intensity=intensity,
                                    resting_heart_rate=resting_heart_rate, exercise_heart_rate=exercise_heart_rate,
                                    body_fat_percentage=body_fat_percentage, muscle_mass=muscle_mass, water_intake=water_intake)

    else:
        return render_template('user_activity.html')

@app.route('/stats', methods=['GET'])
@login_required
def stats():
     # Get the logged-in user's ID
    user_id = session.get("user_id")

    stats_data = []

    distinct_user_activity_data = get_distinct_user_activity_data(db, user_id)
    latest_user_activity = get_latest_user_activity(db, user_id)
    user_activities = get_all_user_activity(db, user_id)
    user_activities_sorted = get_all_user_activity_by_registered_at_desc(db, user_id)

    if not distinct_user_activity_data or not latest_user_activity or not user_activities or not user_activities_sorted:
        stats_data = None
        return render_template('stats.html', stats=stats_data)

    age, gender = get_age_and_gender(distinct_user_activity_data)
    body_fat_percentage, muscle_mass = get_latest_bodyfat_and_bodymass(latest_user_activity)
    weight_kg, height_cm = get_latest_weight_and_height(latest_user_activity)


    if height_cm is not None:
        healthy_weight_range_result = calculate_healthy_weight_range(height_cm)
    else:
        healthy_weight_range_result = None

    if healthy_weight_range_result:
        healthy_weight_range_str = "{:.1f}kg - {:.1f}kg".format(*healthy_weight_range_result)
    else:
        healthy_weight_range_str = None
        stats_data = None

    daily_water_intake = calculate_daily_water_intake(latest_user_activity)
    user_water_intake = get_latest_user_water_intake(latest_user_activity)
    # Calculate weight difference
    weight_difference = calculate_weight_difference(user_activities_sorted)
    # Create weight plot
    weight_plot_data = create_weight_plot(user_activities)
    bmi, bmi_category_result = calculate_bmi_and_category(weight_kg, height_cm)
    # Create bmi plot
    bmi_plot_data = create_bmi_plot(user_activities)

    if not weight_plot_data or not bmi_plot_data:
        return render_template('stats.html', stats=None)

    stats_data.append({'index': 0, 'graph_data': weight_plot_data})
    stats_data.append({'index': 1, 'graph_data': bmi_plot_data})

    # Convert activities to a list of dictionaries
    activities = []

    for activity in user_activities_sorted:
        activity_data = {
            "activity_type": activity["activity_type"].capitalize(),
            "duration": activity["duration"],
            "intensity": activity["intensity"].capitalize(),
            "resting_heart_rate": activity["resting_heart_rate"],
            "exercise_heart_rate": activity["exercise_heart_rate"],
            "registered_at": activity["registered_at"]
        }
        activities.append(activity_data)

    return render_template('stats.html', stats=stats_data, age=age, gender=gender, body_fat_percentage=body_fat_percentage, muscle_mass=muscle_mass, weight=weight_kg, height=height_cm, bmi=bmi, bmi_category=bmi_category_result, healthy_weight_range=healthy_weight_range_str, weight_difference=weight_difference, daily_water_intake=daily_water_intake, user_water_intake=user_water_intake, activities=activities)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name'].capitalize()
        email = request.form['email']
        subject = request.form['subject'].capitalize()
        phone = request.form['phone']
        message = request.form['message'].capitalize()

        messages = []

        validate_contact_inputs(name, "Name", messages)
        validate_email(email, messages)
        validate_contact_inputs(subject, "Subject", messages)
        validate_contact_inputs(phone, "Phone", messages)
        validate_contact_inputs(message, "Message", messages)

        if not messages:
            message_added = db.execute("INSERT INTO contacts (name, email, subject, phone, message) VALUES (?, ?, ?, ?, ?)", name, email, subject, phone, message)

            if not message_added:
                messages.append(("danger",  "There was a problem submitting your message. Please try again!"))
                return render_template('contact.html', messages=messages)

            else:
                messages.append(("success",  "Thank you for your message!"))

                flash(messages[-1])

                # Redirect the user to the home page
                return redirect("/")
        else:
            # Flash the error messages
            for error in messages:
                flash(error)
            return render_template('contact.html', messages=messages, name=name, email=email, subject=subject, phone=phone, message=message)

    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)