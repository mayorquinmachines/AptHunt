#!/usr/bin/env
import os

GOOGLE_MAPS_KEY = 'YOUR-GOOGLE-MAPS-KEY'
PROJECT_PATH = os.getcwd() + '/'
CL_bucket_name = 'yourbucketname'
#using the us-west-2 region 
CL_bucket_path = 'https://s3-us-west-2.amazonaws.com/' + CL_bucket_name + '/'

#Areas to commute
dest_coord_UCB = '37.8719034,-122.2607286'
dest_coord_redwood = '37.4997475,-122.2970704'

MAX_PRICE = 2000
MIN_PRICE = 1000
PETS = True
SITE ='sfbay'
AREA ='eby'
CATEGORY ='apa'
LIMIT = 500

NEIGHBORHOODS = ["berkeley north", "berkeley", "walnut creek", "emeryville", "oakland", "concord / pleasant hill / martinez","pleasanton", "livermore","north oakland", "downtown oakland", "redwood city"]

USERS = ['t', 's']
