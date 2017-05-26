#!/usr/bin/env
import urllib, os
import time
import subprocess
import re
import sys
import string
import requests
from lxml import html
import pandas as pd
import boto3
from craigslist import CraigslistHousing
from geopy.distance import vincenty
from boto3.dynamodb.conditions import Key, Attr
import simplejson
from config import *
from decimal import Decimal


#Apt hunt directory
SaveLoc = "/home/kirk/Documents/ML_learning_materials/apt_hunt/"
#key for google maps 
key = "&key=" + GOOGLE_MAPS_KEY
#Areas to commute
dest_coord_UCB = '37.8719034,-122.2607286'
dest_coord_redwood = '37.4997475,-122.2970704'

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('apthunt')

#initializing bounding boxes and BARF vicinity info
data = [x for x in open('/home/kirk/Documents/ML_learning_materials/apt_hunt/bbox.csv', 'r')]
BOXES = {i: data[i].strip('\n').split(',') for i in range(len(data))}

transit_df = pd.read_csv('/home/kirk/Documents/ML_learning_materials/apt_hunt/BARF.csv', index_col=0, dtype=str)
transit_df['coords'] = zip(transit_df.station_lat.values, transit_df.station_lng.values)
TRANSIT_STATIONS = transit_df[['coords']].to_dict()['coords']

### Helper Functions ####
def in_box(coords, box):
    if box[0][0] < coords[0] < box[1][0] and box[1][1] < coords[1] < box[0][1]:
        return True
    return False

def empties(x):
    if x:
        return x
    else:
        return '-'

def text_extractor(text):
    text_features = {}
    #pre-process text
    text = text.lower()
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'[.,)(*:]', '', text)
    sq_lst = empties(re.search(r'\d+ sq', text).group().split()[0] if re.search(r'\d+ sq', text) else None)
    text_features['sq_lst'] = sq_lst

    bdrm_lst = empties(re.search(r'\d+ (bdrm|bed|room)', text).group()[0] if re.search(r'\d+ (bdrm|bed|room)', text) else None)
    text_features['sq'] = sq_lst

    pet_rent = empties(re.search(r'\d pet deposit|\d pet rent', text).group() if re.search(r'\d pet deposit|\d pet rent',text) else None)
    text_features['pet_rent'] = pet_rent

    pool = Decimal(int('pool' in text))
    text_features['pool'] = pool

    laundry = Decimal(int('laundry' in  text))
    text_features['laundry'] = laundry

    apt = Decimal(int('apartment' in text))
    text_features['apt'] = apt

    cond = Decimal(int('condo' in text))
    text_features['cond'] = cond

    stud = Decimal(int('studio' in text))
    text_features['stud'] = stud

    plex = Decimal(int('plex' in text))
    text_features['plex'] = plex

    house = Decimal(int('house' in text))
    text_features['house'] = house

    park = Decimal(int('park' in text))
    text_features['park'] = park

    return text_features

    

def drive_times(geotag, destination):
    gmaps_url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(",".join(geotag), destination)
    res_dest = simplejson.load(urllib.urlopen(gmaps_url))
    driving_time = res_dest['rows'][0]['elements'][0]['duration']['text']
    return driving_time

def GetStreet(Add, SaveLoc, name):
    base = "https://maps.googleapis.com/maps/api/streetview?size=1200x800&location="
    Add = ','.join(Add)            # pass lat/lng instead of street address
    MyUrl = base + Add + key
    urllib.urlretrieve(MyUrl, os.path.join(SaveLoc, name))    # replace with storage to S3 bucket
##########################


#Max budget == 2000, minimum== 1000 (want an apartment not room), dog friendly
cl_h = CraigslistHousing(site='sfbay', area='eby', category='apa', filters={'max_price': 2000, 'min_price': 1000, 'dogs_ok':True})

#Results for loop
for result in cl_h.get_results(sort_by='newest', geotagged=True, limit=1000):
    try:
        os.mkdir(result['id'])
        if result['geotag'] != None:
            geotag = map(str, result['geotag'])
        else:
            geotag = result['geotag']
        
        #Checking if it is in prefered area
        area_found = False
        area = ""
        for a, coords in BOXES.items():
            coords = [map(str, bx) for bx in coords]
            try:
                if in_box(geotag, coords):
                    area = a
                    area_found = True
            except:
                pass

        #Checking Neighborhood in case there's no geotag
        NEIGHBORHOODS = ["berkeley north", "berkeley", "walnut creek", "emeryville", "oakland", "concord / pleasant hill / martinez"
                        ,"pleasanton", "livermore","north oakland", "downtown oakland", "redwood city"]
        location = result["where"]
        if not area and location:
            for hood in NEIGHBORHOODS:
                if hood in location.lower():
                    area = hood

        #If ad satisfies bounding box or neighborhood
        if area_found or area:
            #Finding nearest BARF 
            #os.mkdir(result['id'])
            if geotag:
                min_dist = 100
                for station, coords in TRANSIT_STATIONS.items():
                   BART_dist = vincenty(coords, geotag)
                   if BART_dist < min_dist:
                       min_dist = BART_dist
                       min_dist = min_dist.miles
                       close_stn = station

                try:
                    #Traffic time
                    driving_time_red = drive_times(geotag, dest_coord_redwood)
                    driving_time_ucb = drive_times(geotag, dest_coord_UCB)
                except:
                    driving_time_red = None
                    driving_time_ucb = None

                #retrieving google maps picture
                pic_name = 'streetview_' + str(result["id"]) + '.jpg' 
                GetStreet(geotag, '/'.join([SaveLoc, result['id']]), pic_name) 
                #upload pic to s3 and get url
                streetpic_url = 'https://s3-us-west-2.amazonaws.com/apthunt/' + pic_name
            else:
                min_dist = None
                close_stn = None
                driving_time_red = None
                driving_time_ucb = None
                pic_name = None
                streetpic_url = None

            #Getting text
            page = requests.get(result["url"])
            tree = html.fromstring(page.content)
            pg_txt = tree.xpath('//section[@id="postingbody"]/text()')
            pg_txt = [x.replace('\n', '').strip() for x in pg_txt]
            pg_txt = ' '.join([x for x in pg_txt if x])

            ##### Extracting features from text #######
            corpus = str(result['name'].encode('utf-8')) + pg_txt.encode('utf-8') 
            txt_dict = text_extractor(corpus)

            ###########################################


            #Getting all pics from post
            page = requests.get(result["url"])
            tree = html.fromstring(page.content)
            imgs_pth = tree.xpath('//div[@id="thumbs"]//a/@href')
            for i, imgs in enumerate(imgs_pth):
                #wget_com = "wget " + imgs + " > " + SaveLoc + str(result['id'])+ "/" + str(result['id']) + "_"+ str(i) + ".jpg" 
                wget_com = "wget " + "-O " + SaveLoc + str(result['id'])+ "/" + str(result['id']) + "_"+ str(i) + ".jpg " + imgs 
                subprocess.call(wget_com, shell=True)

            subprocess.call("aws s3 sync ./%s s3://apthunt/ --acl public-read" %result['id'], shell=True)

            #Getting all picture links
            try:
                pic_links = ['https://s3-us-west-2.amazonaws.com/apthunt/'+result['id']+'_' + str(i) for i in enumerate(imgs_pth)]
                if streetpic_url != '-':
                    pic_links.append(streetpic_url)
                pic_links = '|'.join(pic_links)
            except:
                pic_links = '-'
            Item_dict = {'id': empties(result["id"]), 'price':empties(result["price"]),
                                 'url':empties(result["url"]), 'area':empties(result["where"]),  
                                 'name':empties(result["name"]),'barf_dist': empties(str(min_dist)),
                                 'barf_loc':empties(close_stn), 'ucb_dist':empties(driving_time_ucb), 
                                 'red_dist': empties(driving_time_red), 'pic_links':empties(pic_links),
                                 'post_txt':empties(pg_txt), 't_seen': Decimal(0), 't_like': Decimal(0),
                                 's_seen':Decimal(0), 's_like':Decimal(0)}
            Item_dict.update(txt_dict)
            #Adding all info to dynamodb table
            table.put_item(Item=Item_dict)
    except OSError:
        pass
# Pass unread to SQS
def sqs_push(attr):
    response = table.scan(FilterExpression=Attr(attr + '_seen').eq(0))
    item_ids = [cl_post['id'] for cl_post in response['Items']]
    try:
        queue = sqs.get_queue_by_name(QueueName=attr + '_apthunt')
        queue.delete()
    except:
        pass
    time.sleep(65)
    queue = sqs.create_queue(QueueName=attr + '_apthunt')
    for itm in item_ids:
        response = queue.send_message(MessageBody=itm)
    return 

sqs = boto3.resource('sqs')
sqs_push('t')
sqs_push('s')
