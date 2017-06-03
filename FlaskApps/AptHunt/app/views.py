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


dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
#I map the user ids to initials to map user a and user b preferences. 
#Add more users or change the initials to your liking
user_dic = {'1':'a', '2':'b'}
table = dynamodb.Table('yourtablename')

@app.route('/', methods = ['GET', 'POST'])
@login_required
def apthunt():
    user = str(current_user.get_id())
    seen_col = user_dic[user]+'_seen'
    posts = table.scan(FilterExpression=Attr(seen_col).eq(0))['Items'][:100] 
    ids_lst = [str(x['id']) for x in posts]
    for post in posts:
        post['a_seen'] = int(post['a_seen'])
        post['b_seen'] = int(post['b_seen'])
        post['a_like'] = int(post['a_like'])
        post['b_like'] = int(post['b_like'])
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
        update_express = "set " + like_col + " = :val1, " + seen_col + " = :val2" 
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
