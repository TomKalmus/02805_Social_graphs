# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 19:11:53 2014

@author: tomek
"""

import twitter
import json
import pymongo
from urllib2 import URLError
from httplib import BadStatusLine
import sys
import time

def oauth_login():
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

'''
Functions for saving and retrieving data from mongoDB
'''
def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    # Connects to the MongoDB Server running on
    # localhost:27017 by default
    
    client = pymongo.MongoClient(**mongo_conn_kw)
    
    # Get a reference to a particular database
    db = client[mongo_db]
    
    # Reference a particular collection in the database
    coll = db[mongo_db_coll]
    
    # Perform a bulk insert and return the IDs
    return coll.insert(data)

def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False,
                    criteria=None, projection=None, **mongo_conn_kw):
    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    # Consider leveraging MongoDB's aggregations framework for more
    # sophisticated queries.
    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    
    if criteria is None:
        criteria = {}
        
    if projection is None:
        cursor = coll.find(criteria)
    else:
        cursor = coll.find(criteria, projection)
        
    # Returning a cursor is recommended for large amounts of data
    
    if return_cursor:
        return cursor
    else:
        return [ item for item in cursor ]

    
'''
Function for making secure twitter request, avoiding any errors
1) Nested function taking as argument http error code and wait period (in seconds)
2) Loop for trying to call the function and catching eventual errors. Errors are sent to the
nested function, which returns time to put process to sleep, after which retries. If number of retries
too big => screw it
'''
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600:
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
        
        if e.e.code == 401:
            print >> stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e
            
    wait_period = 2
    error_count = 0
    
    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

'''
Function to get tweets from my timeline. Gets number of tweets to retrieve and a mechanism to overcome the count
limit of the API. These are the following steps:
    1) Specify arguments for API function (kw)
    2) Specify number of pages with tweets to retrieve
    3) Run the function using the safe method implemented before
    4) Fetch the results of the function to the results list
    5) Check if counts given to function not smaller than API enables to prevent loop entry
    6) In loop get tweets as long as the limits have not been reached
    7) return list with tweets
'''

def harvest_home_timeline(twitter_api, max_results=1000):
    kw = {  # Keyword args for the Twitter API call
        'count': 200,
        'trim_user': 'true',
        'since_id' : 1
        }
    
    max_pages = 16
    results = []
    
    tweets = make_twitter_request(twitter_api.statuses.home_timeline, **kw)
    
    # ["text"], ["coordinates"], ["retweet_count"], ["id"], ["created_at"], ["user"]["id"]
    if tweets is None: # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []
    
    tweets_processed = [ dict([('text', tweet["text"]), ('coordinates', tweet["coordinates"]), 
                               ('retweet_count', tweet["retweet_count"]), ('id', tweet["id"]), 
                              ('created_at', tweet["created_at"]), ('user_id', tweet["user"]["id"])
                              ]) for tweet in tweets]

    results += tweets_processed
    
    print >> sys.stderr, 'Fetched %i tweets' % len(tweets_processed)
    
    page_num = 1
    
    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry
    
    while page_num < max_pages and len(tweets_processed) > 0 and len(results) < max_results:
    
        # Necessary for traversing the timeline in Twitter's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.
        kw['max_id'] = min([ tweet['id'] for tweet in tweets_processed]) - 1 
    
        tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
        
        tweets_processed = [ dict([('text', tweet["text"]), ('coordinates', tweet["coordinates"]), 
                               ('retweet_count', tweet["retweet_count"]), ('id', tweet["id"]), 
                              ('created_at', tweet["created_at"]), ('user_id', tweet["user"]["id"])
                              ]) for tweet in tweets]
        
        results += tweets_processed

        print >> sys.stderr, 'Fetched %i tweets' % (len(tweets_processed),)
    
        page_num += 1
        
    print >> sys.stderr, 'Done fetching tweets'

    return results[:max_results]
    
# def get_home_timeline(twitter_api, count=2, since_id=None, exclude_replies=True):
#    search_results = twitter_api.statuses.home_timeline(count=count)
#    
#    return search_results

twitter_api = oauth_login()
results = harvest_home_timeline(twitter_api)

save_to_mongo(results, 'search_results', 'tweets')
# load_from_mongo('search_results', 'tweets')
