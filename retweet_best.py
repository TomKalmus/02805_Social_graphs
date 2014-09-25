import twitter
import json
import pymongo
from pymongo import Connection

def oauth_login():
    CONSUMER_KEY = 'CyAip6p31NAft9oaxzOQ6oB8J'
    CONSUMER_SECRET = 'SQNoR3rSI48CQJNRp0JiYvtjUbO8N92vOp2E6FaziqWs41ZmaQ'
    OAUTH_TOKEN = '2787485978-M79tv9HsEksFY4CiVDcFyUaU966coOAbILBvjaH'
    OAUTH_TOKEN_SECRET = 'Nb47C3HKCqZbCSymCos43R0p2T2W6apMp0PYfaQPTl1Qq'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

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
    
def get_timeline_from_database():
    data = [ dict([('tweet_id', item["id"]), ('retweet_count', item["retweet_count"]), 
                   ('text', item["text"])])
                for item in load_from_mongo('search_results', 'tweets') ]    
    return data

def get_max_retweeted(data, retweet_id=None): 
    if retweet_id:
        i = [ data.index(tweet) for tweet in data if tweet["tweet_id"] == retweet_id ]
        del data[i[0]]
    
    retweet_count_list = [ tweet["retweet_count"] for tweet in data ]
    max_value = max(retweet_count_list)
    max_tweet = [ tweet for tweet in data if tweet["retweet_count"] == max_value ]
    
    return max_tweet

def retweet_best_tweet(twitter_api, tweet):
    if tweet is None:
        return
    
    try:
        retweeted = twitter_api.statuses.retweet(id=tweet["tweet_id"])
        return True
    
    except Exception, e:
        print "ERRooorr," , e
        return False  

    
twitter_api = oauth_login()

data = get_timeline_from_database()

if len(data) > 0:
    best_tweet = get_max_retweeted(data)
    Success = retweet_best_tweet(twitter_api, best_tweet[0])
    
    if not Success:
        for i in range(10):
            try:
                best_tweet = get_max_retweeted(data, retweet_id=best_tweet[0]["tweet_id"])                
                Success = retweet_best_tweet(twitter_api, best_tweet[0])
                
                if Success:
                    break
                
            except Exception, e:
                print "Thrown Exception", e

c = Connection()
c['search_results'].drop_collection('tweets')
