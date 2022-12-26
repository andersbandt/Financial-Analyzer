from flask import Blueprint, redirect, url_for, flash, render_template, request,jsonify
from flask_login import current_user, login_user, logout_user, login_required
from main import bcrypt, db
from main.models import User,Transactions
import csv
import datetime

# from main.users.forms import RegistartionForm, LoginForm, UpdateAccountForm
# from main.users.util import save_picture

users = Blueprint('users',__name__)

#This route is for user register, and it can handle both GET and POST requests
@users.route("/register", methods=['GET', 'POST'])
def register():

    # If the user is already authenticated, redirect them to the home page
    # if current_user.is_authenticated:
    #     return redirect(url_for('util.home'))

    # If the request method is POST, this means the user has submitted the registration form
    if request.method == 'POST':
        # Retrieve the submitted form data from the request object
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        # Check if a user with the given email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # If a user with the given email is found, return an error message indicating that the email is already registered
            return jsonify('Error: Email is already registered')

        # Hash the password for security before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new User object with the form data and hashed password
        user = User(username=username, email=email, password=hashed_password)

        # Add the new user to the database session and commit the changes
        db.session.add(user)
        db.session.commit()

        # Return a response indicating that the user was added successfully
        resp = {'response': 'User has been added successfully'}
        return jsonify(resp)

    # If the request method is not POST (e.g. GET), return a JSON object
    return jsonify("{'Hello':'World'}")

#This route is for user login, and it can handle both GET and POST requests
@users.route("/login", methods=['GET', 'POST'])
def login():

    # If the user is already authenticated, return a message indicating that they are already logged in
    if current_user.is_authenticated:
        return jsonify("{'Account already signed in'}")

    # If the request method is POST, this means the user has submitted the login form
    if request.method == 'POST':
        # Retrieve the submitted form data from the request object
        email = request.json['email']
        password = request.json['password']

        # Query the database for a user with the given email
        user = User.query.filter_by(email=email).first()

        # If a user with the given email was found and the password is correct, log the user in
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            # next_page = request.args.get('next')
            return jsonify("user logged in")
        else:
            # If the email or password is incorrect, return a message indicating login was unsuccessful
            return jsonify('Login Unsuccessful. Please check email and password')

    # If the request method is not POST (e.g. GET), return a JSON object
    return jsonify("{'Hello':'World'}")

#This route is for logging out a user
@users.route("/logout")
def logout():
    logout_user()
    return jsonify("user logged out")


@users.route('/upload',methods = ['POST'])
@login_required
def upload():
    # Check if user is authenticated
    if current_user.is_authenticated:
        # Open 'Transactions_sample.csv' in read mode
        with open('Transactions_sample.csv', 'r') as f:
            # Create CSV reader object
            reader = csv.reader(f)
            # Iterate over rows in CSV file
            for row in reader:
                # Create new Transactions object with data from row
                record = Transactions(transaction_date=datetime.datetime.strptime(row[0],"%m/%d/%Y"),amount = row[1], #account_id=row[1],
                              category_id=row[4],user_id=current_user.id)
                # Add object to database session
                db.session.add(record)
        # Commit session to save changes to database
        db.session.commit()
        return 'Table uploaded successfully!'
    else:
        return jsonify("Please sign in")


@users.route("/user/<string:username>")
@login_required
def user_posts(username):
    # Query database for user with specified username
    user = User.query.filter_by(username=username).first_or_404()
    # Query database for transactions associated with user, ordered by transaction date in descending order
    posts = Transactions.query.filter_by(user=user)\
        .order_by(Transactions.transaction_date.desc())
    # Create list of dictionaries with transaction data for each transaction
    posts_list = [post.to_dict() for post in posts]
    # Return list as JSON response, for future use (return chart,table or visualisation)
    return jsonify(posts_list)
