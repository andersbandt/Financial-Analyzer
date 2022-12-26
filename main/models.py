from datetime import datetime
from main import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    # Return user object associated with specified user ID
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    # Define columns for user table in database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    transactions = db.relationship('Transactions', backref='user', lazy='dynamic')

    # Initialization method for User object
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password

    # String representation of User object
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Transactions(db.Model):

    # Define columns for transactions table in database
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.DateTime(100), nullable=False)
    account_id = db.Column(db.Text, nullable=True,default = "Un-assigned")
    category_id = db.Column(db.Text, nullable=True,default = "Un-assigned")
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime(),default = datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # String representation of Transactions object
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

    # Convert Transactions object to dictionary with specified keys
    def to_dict(self):
        return {

            'transaction_date': self.transaction_date,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'date': self.date,
            'user_id': self.user_id,

        }

