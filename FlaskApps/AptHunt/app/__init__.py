from flask import Flask
from flask_mail import Message, Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS

app=Flask(__name__)
app.config.from_object('config')
CORS(app)

mail = Mail()
mail.init_app(app)
db = SQLAlchemy(app)

from app import views, models
from .models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

