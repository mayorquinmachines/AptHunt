from app import app
from .models import User
from flask import Flask
from flask import request, send_from_directory, render_template, redirect, url_for, make_response, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Message, Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_cors import CORS, cross_origin
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key, Attr

"""app=Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'tr0ll@ss'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['DEFAULT_MAIL_SENDER'] = 'contact@ihsotech.com'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = 'L!Zzz@4D4!Nn3RRRRR'
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465 
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "contact@ihsotech.com"
app.config["MAIL_PASSWORD"] = "ch3ckyourselfbeforeyouwreckyourself"
CORS(app)

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
    backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='smayorquin@berkeley.edu', password='turtl3h3@dt3rry')
    user_datastore.create_user(email='terry.j.rodriguez@gmail.com', password='tr0ll0fb3rk3l3y')
    db.session.commit()
"""

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
sqs = boto3.resource('sqs', region_name='us-west-2')
user_dic = {'1':'s', '2':'t'}
table = dynamodb.Table('apthunt')

@app.route('/', methods = ['GET', 'POST'])
@login_required
def apthunt():
    user = str(current_user.get_id())
    seen_col = user_dic[user]+'_seen'
    posts = table.scan(FilterExpression=Attr(seen_col).eq(0))['Items'][:100] 
    ids_lst = [str(x['id']) for x in posts]
    for post in posts:
        post['t_seen'] = int(post['t_seen'])
        post['s_seen'] = int(post['s_seen'])
        post['t_like'] = int(post['t_like'])
        post['s_like'] = int(post['s_like'])
        links = post['pic_links'].split('|')
        links = [x.replace(')', '').replace('(', '').split(',')[0] for x in links]
        links = [x +'.jpg' for x in links if '.jpg' not in x]
        post['pic_links']  = links
    return render_template('index.html', posts=posts, ids_lst =ids_lst)# lst_messages=lst_messages, N=N)

@app.route('/data_like', methods=['GET', 'POST'])
@login_required
@cross_origin()
def data_like():
    user = str(current_user.get_id())
    like_col = user_dic[user] + '_like'
    seen_col = user_dic[user] + '_seen'
    if request.method== 'POST':
	data = request.json['data']
	posts = request.json['ids_lst'].encode('utf-8').strip()
        data = str(bytes(data))
        posts = str(bytes(posts))
        posts = posts.replace('&#39;', '').replace('[', '').replace(']', '')
        posts = posts.split(',')
        posts = [x.strip() for x in posts]
        #now identify proper item for index 
        if int(data) == 0:
            p_id = posts[-1]
        else:
            p_id = posts[int(data)-1]
        #update item in table, process ajax data to correspond with post id
        #table_test = dynamodb.Table('table_test')
	#table_test.put_item(Item={'id': p_id, 'posts': posts, 'ajax_id': data})
        update_express = "set " + like_col + " = :val1, " + seen_col + " = :val2" 
        #table_test.update_item(Key={'id':p_id}, UpdateExpression=update_express, ExpressionAttributeValues={':val1': Decimal(1), ':val2': Decimal(1)}, ReturnValues="UPDATED_NEW")
        table.update_item(Key={'id':p_id}, UpdateExpression=update_express, ExpressionAttributeValues={':val1': Decimal(1), ':val2': Decimal(1)}, ReturnValues="UPDATED_NEW")
    return 'Troll!'

@app.route('/data_dislike', methods=['GET', 'POST'])
@login_required
@cross_origin()
def data_dislike():
    user = str(current_user.get_id())
    like_col = user_dic[user] + '_like'
    seen_col = user_dic[user] + '_seen'
    if request.method== 'POST':
	data = request.json['data']
	posts = request.json['ids_lst'].encode('utf-8').strip()
        data = str(bytes(data))
        posts = str(bytes(posts))
        posts = posts.replace('&#39;', '').replace('[', '').replace(']', '')
        posts = posts.split(',')
        posts = [x.strip() for x in posts]
        #now identify proper item for index 
        if int(data) == 0:
            p_id = posts[-1]
        else:
            p_id = posts[int(data)-1]
        update_express = "set " + like_col + " = :val1, " + seen_col + " = :val2" 
        table.update_item(Key={'id':p_id}, UpdateExpression=update_express, ExpressionAttributeValues={':val1': Decimal(0), ':val2': Decimal(1)}, ReturnValues="UPDATED_NEW")
    return 'Troll!'


"""if __name__ == "__main__":
    app.run()"""
