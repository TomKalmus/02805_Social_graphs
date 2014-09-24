import twitter
import json
import pymongo

def oauth_login():
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

def get_timeline_from_database():
    data = [ dict([('tweet_id', item["id"]), ('retweet_count', item["retweet_count"])])
                for item in load_from_mongo('search_results', 'tweets') ]    
    return data

def get_max_retweeted(data):
    retweet_count_list = [ tweet["retweet_count"] for tweet in data ]
    max_value = max(retweet_count_list)
    max_tweet = [ tweet for tweet in data if tweet["retweet_count"] == max_value ]
    
    return max_tweet

def retweet_best_tweet(twitter_api, tweet):
    if tweet is None:
        return

    retweeted = twitter_api.statuses.retweet(id=tweet["tweet_id"])

twitter_api = oauth_login()

data = get_timeline_from_database()

best_tweet = get_max_retweeted(data)

retweet_best_tweet(twitter_api, best_tweet[0])
