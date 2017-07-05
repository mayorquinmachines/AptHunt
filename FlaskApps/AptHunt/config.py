import os
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import timedelta

WTF_CSRF_ENABLED = True


SECRET_KEY = 'yoursecretkey'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SECURITY_REGISTERABLE = True
DEFAULT_MAIL_SENDER = 'yourgmailaddress@gmail.com'
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'salty'
SECURITY_TRACKABLE = True
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "yourgmailaddress@gmail.com"
MAIL_PASSWORD = "yourgmailpassword"
