#!/bin/bash

sudo apt install python
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo apt-get install python-flask
sudo apt-get install python-pip python-dev build-essential
sudo pip install --upgrade pip

sudo pip install boto3
sudo pip install flask-security flask-sqlalchemy
sudo pip install -U flask-cors
sudo pip install python-crontab
sudo pip install geopy
sudo pip install lxml
sudo pip install requests
sudo pip install simplejson

sudo mv FlaskApps/ /var/www/FlaskApps
sudo mv /var/www/FlaskApps/AptHunt.conf /etc/apache2/sites-available/AptHunt.conf

sudo a2enmod wsgi
sudo apachectl restart
sudo a2ensite AptHunt
sudo service apache2 reload
sudo /etc/init.d/apache2 reload

sudo service apache2 restart
sudo /etc/init.d/apache2 reload
