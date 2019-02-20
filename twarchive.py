# -*- coding: utf-8 -*-
"""
TwEpoch: Twitter Archiver v0.2

The main loop grabs a response from twitter, sorts it based on the most popular
tweets, ("tweet_volume"), and then gets processed and the TOP 10 added to our
daily trends dict.

These trends are given a value of rank and appearances.
At the end of the day, we will calculate the overall most popular, sorting the list similarly to
the twitter response using
        lambda x: x = (rank/appearances)
The lower the number, the more popular it was. More appearances and lower rank number will
increase popularity.

[Note: 1 is most popular rank, 10 is least popular rank.]
[Note 2: This popularity sorting doesn't really need to be done until the javascript phase.]

Currently, this version 0.2 does NOT get any popular tweets from the given hashtag or trend.

When making the website to put these on, we can use JS to open up the json again and sort it out as we need.
"""

import datetime
import json
import math
import sched
import time
import tweepy
import os


# Where On Earth IDs.
# Used to search trends by a specific location.
US_WOEID = 23424977
WORLDWIDE_WOEID = 1
# time to sleep for (seconds)
HOUR = 3600
MINUTE = 60

KEY = ""
SECRET = ""
APP_TOKEN = ""
APP_SECRET = ""


def setup_tweepy():
    """set up and return tweepy client using our env variables"""
    KEY = os.environ.get("KEY", None)
    print(KEY)
    SECRET = os.environ.get("SECRET", None)
    print(SECRET)
    APP_TOKEN = os.environ.get("APP_TOKEN", None)
    print(APP_TOKEN)
    APP_SECRET = os.environ.get("APP_SECRET", None)
    print(APP_SECRET)
    if (KEY != "" and SECRET != "" and APP_TOKEN != "" and APP_SECRET != ""):
        print("Verified Twitter keys.")
    else:
        print("Incorrect environment vars. Shutting down...")
        sys.exit(1);
    auth = tweepy.OAuthHandler(KEY, SECRET)
    auth.set_access_token(APP_TOKEN, APP_SECRET)
    client = tweepy.API(auth, wait_on_rate_limit=True)
    return client

def save_as_json(daily_trends, filename):
    """save a json version of our daily trends to use with other programs"""

    with open(filename, 'w') as fp:
        json.dump(daily_trends, fp)
    fp.close()
    return

def seconds_until_midnight():
    """Get the number of seconds until midnight"""
    tomorrow = datetime.datetime.now() + datetime.timedelta(1)
    midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month,
                        day=tomorrow.day, hour=0, minute=0, second=0)
    return (midnight - datetime.datetime.now()).seconds

def main():

    #prevent the app from saving an empty file at midnight of its first day running.
    first_time_running = True

    client = setup_tweepy()
    daily_trends = {}
    # set up our filename
    filename = datetime.datetime.today().strftime("database/%m_%d_%Y.json")

    #calculate tomorrow's date so we can use it to know when to stop querying.
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    # stop polling right before "tomorrow"
    stop_query = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, 0) - datetime.timedelta(minutes=5)

    print("\nStart running on: " + datetime.datetime.today().strftime("%x") + "\n\n")

    while(1):
        while(datetime.datetime.now() < stop_query):
            print("Calling Twitter")
            twitter_response = sorted(client.trends_place(US_WOEID)[0]['trends'],
                                  key=lambda k: 0 if (not k['tweet_volume']) else (k['tweet_volume']),
                                  reverse=True)
            i = 1
            for e in twitter_response:
                if not (e["name"] in daily_trends):
                    daily_trends[e["name"]] = {"rank"         : i,
                                               "url"          : e["url"],
                                               "tweet_volume" : e["tweet_volume"],
                                               "appearances"  : 1,
                                               "tweets"       : None} # we will get tweets at the beginning of the loop.
                                                                      # when ever i decide to look at the docs.
                else :
                    # add new rank and increment appearances
                    # don't have to be too accurate about tweet_volume, so we can just stick with the last known one for now.
                    daily_trends[e["name"]]["rank"]        += i
                    daily_trends[e["name"]]["appearances"] += 1
                    daily_trends[e["name"]]["tweet_volume"] = e["tweet_volume"]
                i += 1
                if (i == 10):
                    break # FOR LOOP ESCAPE
            #print daily trends to ensure it's still working
            #print daily_trends

            print("\nUpdated. Sleeping until " + (datetime.datetime.today() + datetime.timedelta(hours=1)).strftime("%X") + "\n")
            #prevent data loss during the day x(
            #if we save over the file, it rewrites it, so at the very least we will
            # have half a complete file over nothing at all.
            save_as_json(daily_trends, filename)
            time.sleep(HOUR)
        """
        now we perform our "end of day" tasks
        - save file
        - update date to a new tomorrow
        - sleep for the rest of the day
        """
        if first_time_running:
            first_time_running = False
        else:
            save_as_json(daily_trends, filename)
            daily_trends = {}

        tomorrow = tomorrow + datetime.timedelta(days=1)
        stop_query = tomorrow - datetime.timedelta(minutes=5)
        filename = datetime.datetime.today().strftime("database/%m_%d_%Y.json") 

if __name__ == "__main__":
    """
    Set up a job scheduler to run at Midnight on the day this instance is started
    This will let us have an accurate representation of the day from
    00:00 ==> 23:55
    """
    stm = seconds_until_midnight()
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(stm, 1, main, ());
    print("Script will begin running in " + str(stm) + " seconds.")
    scheduler.run()
