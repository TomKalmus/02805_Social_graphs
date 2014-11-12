import twitter
import matplotlib.pyplot as plt
import sys
from pylab import *

def oauth_login():
    CONSUMER_KEY = 'CyAip6p31NAft9oaxzOQ6oB8J'
    CONSUMER_SECRET = 'SQNoR3rSI48CQJNRp0JiYvtjUbO8N92vOp2E6FaziqWs41ZmaQ'
    OAUTH_TOKEN = '2787485978-M79tv9HsEksFY4CiVDcFyUaU966coOAbILBvjaH'
    OAUTH_TOKEN_SECRET = 'Nb47C3HKCqZbCSymCos43R0p2T2W6apMp0PYfaQPTl1Qq'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

def read_text(path):
    screen_names = open(path).read()
    close(path)
    return screen_names
    

def count_statistics(screen_names, twitter_api, attribute="followers_count"):
    names = [ name for name in screen_names.split('\r\n') if name!='' ]

    counter = []
    page = 1
    screen_names_part = []
    
    if len(names)>99:
        screen_names_part = names[:99]
    else:
        screen_names_part = names
    
    max_page = len(names)/100
    print max_page
    while page<=max_page:
        screen_names_str = ",".join(screen_names_part)
        
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            counter.append(user[attribute])
        
        if page!=max_page:
            screen_names_part = names[page*100:(page + 1)*100]
        else:
            screen_names_part = names[page*100:]
            
        print >> sys.stderr, page
        page += 1
        
    if len(screen_names_part) <= 100 and len(screen_names_part)!=0:
        screen_names_str = ",".join(screen_names_part)
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            counter.append(user[attribute])
        
    return counter

def get_creation_year(screen_names, twitter_api):
    names = [ name for name in screen_names.split('\r\n') if name!='' ]

    years = []
    page = 1
    screen_names_part = []
    
    if len(names)>99:
        screen_names_part = names[:99]
    else:
        screen_names_part = names
    
    max_page = len(names)/100

    while page<=max_page:
        screen_names_str = ",".join(screen_names_part)
        
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            years.append(user["created_at"][-4:])
        
        if page!=max_page:
            screen_names_part = names[page*100:(page + 1)*100]
        else:
            screen_names_part = names[page*100:]
            
        print >> sys.stderr, page
        page += 1
        
    if len(screen_names_part) <= 100 and len(screen_names_part)!=0:
        screen_names_str = ",".join(screen_names_part)
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            years.append(user["created_at"][-4:])
        
    return years

def get_locations(screen_names, twitter_api):
    names = [ name for name in screen_names.split('\r\n') if name!='' ]

    locations = []
    page = 1
    screen_names_part = []
    
    if len(names)>99:
        screen_names_part = names[:99]
    else:
        screen_names_part = names
    
    max_page = len(names)/100

    while page<=max_page:
        screen_names_str = ",".join(screen_names_part)
        
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            locations.append(user["location"])
        
        if page!=max_page:
            screen_names_part = names[page*100:(page + 1)*100]
        else:
            screen_names_part = names[page*100:]
            
        print >> sys.stderr, page
        page += 1
        
    if len(screen_names_part) <= 100 and len(screen_names_part)!=0:
        screen_names_str = ",".join(screen_names_part)
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            locations.append(user["location"])
        
    return locations


def get_descriptions(screen_names, twitter_api):
    names = [ name for name in screen_names.split('\r\n') if name!='' ]

    descriptions = []
    page = 1
    screen_names_part = []
    
    if len(names)>99:
        screen_names_part = names[:99]
    else:
        screen_names_part = names
    
    max_page = len(names)/100

    while page<=max_page:
        screen_names_str = ",".join(screen_names_part)
        
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            descriptions.append(user["description"])
        
        if page!=max_page:
            screen_names_part = names[page*100:(page + 1)*100]
        else:
            screen_names_part = names[page*100:]
            
        print >> sys.stderr, page
        page += 1
        
    if len(screen_names_part) <= 100 and len(screen_names_part)!=0:
        screen_names_str = ",".join(screen_names_part)
        users = twitter_api.users.lookup(screen_name=screen_names_str)
        
        for user in users:
            descriptions.append(user["description"])
        
    return descriptions

def draw_histogram(list1, list2=None, limit=20000, bins=100, title="Followers histogram"):
    if limit:
        local_list = [ item for item in list1 if item < limit ]
    else:
        local_list = list1
    
    figure(figsize=(14,9))
    plt.hist(local_list, bins=bins, histtype='stepfilled', color='b')
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    
    if list2:
        if limit:
            local_list2 = [ item for item in list2 if item < limit ]
        else:
            local_list2 = list2
        
        plt.hist(local_list2, bins=bins, histtype='stepfilled', color='r', alpha=0.5)
        plt.legend(['didntfollowback', 'followed'])
        
    plt.show()


# twitter_api = oauth_login()
# screen_names = read_text('didntfollowback.txt')
# num_followers = count_statistics(screen_names, twitter_api)
# screen_names2 = read_text('followed.txt')
# num_followers2 =  count_statistics(screen_names2, twitter_api)
draw_histogram(num_followers, list2=num_followers2, limit=500, bins=20)
# num_friends = count_statistics(screen_names, twitter_api, attribute="friends_count")
# num_friends2 = count_statistics(screen_names2, twitter_api, attribute="friends_count")
# draw_histogram(num_friends, list2=num_friends2, limit=5000, bins=50, title="Friends histogram")
# num_tweet = count_statistics(screen_names, twitter_api, attribute="statuses_count")
# num_tweet2 = count_statistics(screen_names2, twitter_api, attribute="statuses_count")
# draw_histogram(num_tweet, list2=num_tweet2, limit=5000, bins=50, title="Tweets histogram")
#print get_locations(screen_names2, twitter_api)
