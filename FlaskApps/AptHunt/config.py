import os
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import timedelta


DEBUG = True
SECRET_KEY = 'yoursecretkey'
SECURITY_REGISTERABLE = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' 
DEFAULT_MAIL_SENDER = 'yourgmailaddress@gmail.com'
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'salty'
SECURITY_TRACKABLE = True
SEND_REGISTER_EMAIL = False
SECURITY_RECOVERABLE = True
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "yourgmailaddress@gmail.com"
MAIL_PASSWORD = "yourgmailpassword"
