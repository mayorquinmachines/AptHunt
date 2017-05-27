#!/usr/bin/env
""" helper_funcs module contains all functions needed for craigslist_scrapper.py"""
import os
import time
import urllib
import re
from decimal import Decimal
import requests
from lxml import html
import simplejson
from boto3.dynamodb.conditions import Attr


def in_box(coords, box):
    """ Returns True if a geotag is inside a specified coordinate box"""
    if box[0][0] < coords[0] < box[1][0] and box[1][1] < coords[1] < box[0][1]:
        return True
    return False

def empties(item):
    """ Helper function to format NoneTypes into dashes"""
    if item:
        return item
    else:
        return '-'

def text_extractor(result):
    """ Helper function to return all data from html page """
    #getting page content
    page = requests.get(result["url"])
    tree = html.fromstring(page.content)
    #retrieving pic links
    imgs_pth = tree.xpath('//div[@id="thumbs"]//a/@href')
    #retrieving text
    pg_txt = tree.xpath('//section[@id="postingbody"]/text()')
    pg_txt = [x.replace('\n', '').strip() for x in pg_txt]
    pg_txt = ' '.join([x for x in pg_txt if x])
    text = str(result["name"].encode("utf-8")) + pg_txt.encode("utf-8")
    text_features = {}
    #pre-process text
    text = text.lower()
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'[.,)(*:]', '', text)
    sq_lst = empties(re.search(r'\d+ sq', text).group().split()[0] \
                     if re.search(r'\d+ sq', text) else None)
    text_features['sq_lst'] = sq_lst

    bdrm_lst = empties(re.search(r'\d+ (bdrm|bed|room)', text).group()[0] \
                       if re.search(r'\d+ (bdrm|bed|room)', text) else None)
    text_features['bdrm_lst'] = bdrm_lst

    pet_rent = empties(re.search(r'\d pet deposit|\d pet rent', text).group() \
                       if re.search(r'\d pet deposit|\d pet rent', text) else None)
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

    return text_features, text, imgs_pth

def drive_times(geotag, destination):
    """ Returns driving time estimation for UCB distances and Redwood city distances """
    gmaps_url = "http://maps.googleapis.com/maps/api/distancematrix/json?"\
                "origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(",".join(geotag), destination)
    res_dest = simplejson.load(urllib.urlopen(gmaps_url))
    driving_time = res_dest['rows'][0]['elements'][0]['duration']['text']
    return driving_time

#change in scrapper.py file
def get_street(added, save_loc, name, key):
    """ Helper function for downloading street view photo for geotag """
    base = "https://maps.googleapis.com/maps/api/streetview?size=1200x800&location="
    added = ','.join(added)
    my_url = base + added + key
    urllib.urlretrieve(my_url, os.path.join(save_loc, name))

def sqs_push(attr, bucket_name, table):
    """ Helper Function to create user queues """
    response = table.scan(FilterExpression=Attr(attr + '_seen').eq(0))
    item_ids = [cl_post['id'] for cl_post in response['Items']]
    app_queue = '_' + bucket_name
    try:
        queue = sqs.get_queue_by_name(QueueName=attr + app_queue)
        queue.delete()
    except:
        pass
    time.sleep(65)
    queue = sqs.create_queue(QueueName=attr + app_queue)
    for itm in item_ids:
        response = queue.send_message(MessageBody=itm)
    return
