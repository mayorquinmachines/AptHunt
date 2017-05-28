#!/bin/bash

sudo apt install python
sudo apt-get install apache2
sudo apt-get update
sudo apt-get install libapache2-mod-wsgi
sudo apt-get install python-flask
sudo apt-get upgrade
sudo apt-get python-pip

sudo pip install boto3
sudo pip install python-crontab
sudo pip install geopy
sudo pip install lxml
sudo pip install requests
sudo pip install simplejson

sudo mv FlaskApps/ /var/www/FlaskApps
sudo mv /var/www/FlaskApps/AptHunt.conf /etc/apache2/sites-available/AptHunt.conf

sudo a2enmod wsgi
sudo apachectl restart
sudo a2ensite PlagiarismDefenderApp
sudo service apache2 reload
sudo /etc/init.d/apache2 reload

sudo service apache2 restart
/etc/init.d/apache2 reload

