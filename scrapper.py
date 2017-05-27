#!/usr/bin/env
""" Apt Hunt main loop to load Craigslist Ad data into AWS S3 and DynamoDB"""
import os
import urllib
import subprocess
from decimal import Decimal
import csv
import boto3
from craigslist import CraigslistHousing
from geopy.distance import vincenty
import craigslist_config as cc
import helper_funcs as helpers

#google maps api key
API_KEY = "&key=" + cc.GOOGLE_MAPS_KEY

DYNAMODB = boto3.resource('dynamodb')
TABLE = DYNAMODB.Table(cc.CL_bucket_name)

#initializing bounding boxes and BARF distance
BBOXES = [x for x in open(cc.PROJECT_PATH + 'bbox.csv', 'r')]
BOXES = {i: BBOXES[i].strip('\n').split(',') for i in range(len(BBOXES))}

BARF_STNS = []
with open(PROJECT_PATH + 'BARF.csv', 'r') as csvfile:
    datareader = csv.reader(csvfile, delimiter=',')
    header = next(datareader)
    for row in datareader:
        BARF_STNS.append(row)
TRANSIT_STATIONS = {barf[0]: tuple(barf[1:]) for barf in BARF_STNS}


CL_ADS = CraigslistHousing(site=cc.SITE, area=cc.AREA, category=cc.CATEGORY,
                           filters={'max_price': cc.MAX_PRICE, 'min_price': cc.MIN_PRICE,
                                    'dogs_ok': cc.PETS})

for result in CL_ADS.get_results(sort_by='newest', geotagged=True, limit=cc.LIMIT):
    try:
        os.mkdir(result['id'])
        if result['geotag'] != None:
            geotag = map(str, result['geotag'])
        else:
            geotag = result['geotag']
        area_found = False
        area = ""
        for a, coords in BOXES.items():
            coords = [map(str, bx) for bx in coords]
            try:
                if helpers.in_box(geotag, coords):
                    area = a
                    area_found = True
            except:
                pass

        location = result["where"]
        if not area and location:
            for hood in cc.NEIGHBORHOODS:
                if hood in location.lower():
                    area = hood

        if area_found or area:
            if geotag:
                min_dist = 100.
                for station, coords in TRANSIT_STATIONS.items():
                    BART_dist = vincenty(coords, geotag)
                    BART_dist = BART_dist.miles
                    if BART_dist < min_dist:
                        min_dist = BART_dist
                        close_stn = station

                try:
                    driving_time_red = helpers.drive_times(geotag, cc.dest_coord_redwood)
                    driving_time_ucb = helpers.drive_times(geotag, cc.dest_coord_UCB)
                except:
                    driving_time_red = None
                    driving_time_ucb = None

                #retrieving google maps picture
                pic_name = 'streetview_' + str(result["id"]) + '.jpg'
                helpers.get_street(geotag, '/'.join([cc.PROJECT_PATH, result['id']]), pic_name, API_KEY)
                streetpic_url = cc.CL_bucket_path + pic_name

            #retrieving all data from html page
            txt_dict, pg_txt, imgs_pth = helpers.text_extractor(result)

            ###########################################

            #Getting all pics from post
            for i, imgs in enumerate(imgs_pth):
                wget_com = "wget " + "-O " + cc.PROJECT_PATH + str(result['id'])+ "/" + \
                            str(result['id']) + "_"+ str(i) + ".jpg " + imgs
                subprocess.call(wget_com, shell=True)
            cmd = "aws s3 sync ./%s s3://%s/ --acl public-read" %(result['id'], cc.CL_bucket_name)
            subprocess.call(cmd, shell=True)

            #Getting all picture links
            try:
                pic_links = [cc.CL_bucket_path + result['id'] + '_' + \
                             str(i) for i in enumerate(imgs_pth)]
                if streetpic_url != '-':
                    pic_links.append(streetpic_url)
                pic_links = '|'.join(pic_links)
            except:
                pic_links = '-'

            item_keys = ['id', 'price', 'url', 'where', 'name']
            item_vals = map(helpers.empties, [result[i] for i in item_keys])
            Item_dict = {item_keys[i]: item_vals[i] for i in range(len(item_keys))}

            var_keys = ['barf_dist', 'barf_loc', 'ucb_dist', \
                        'red_dist', 'pic_links', 'post_txt']
            var_vals = map(helpers.empties, [str(min_dist), close_stn, driving_time_ucb,\
                                     driving_time_red, pic_links, pg_txt])
            var_dict = {var_keys[i]: var_vals[i] for i in range(len(var_keys))}
            Item_dict.update(var_dict)

            item_keys_num = ['t_seen', 't_like', 's_seen', 's_like']
            Item_dict_num = {item_keys_num[i]: Decimal(0) for i in range(len(item_keys_num))}
            Item_dict.update(Item_dict_num)
            Item_dict.update(txt_dict)
            TABLE.put_item(Item=Item_dict)
    except OSError:
        pass

#pass to sqs
#sqs = boto3.resource('sqs')
#[helpers.sqs_push(x, cc.CL_bucket_name, TABLE) for x in cc.USERS]
