import tweepy

# Where On Earth IDs.
# Used to search trends by a specific location.
US_WOEID = 23424977
WORLDWIDE_WOEID = 1

def main():
    keyfile = open('keys', 'r')

    key = keyfile.readline().strip()
    secret = keyfile.readline().strip()

    auth = tweepy.OAuthHandler(key, secret)

    app_token = keyfile.readline().strip()
    app_secret = keyfile.readline().strip()

    auth.set_access_token(app_token, app_secret)

    keyfile.close()

    client = tweepy.API(auth, wait_on_rate_limit=True)
    response_dict = client.trends_place(US_WOEID)[0]['trends']


    # sort by "tweet_volume". There are our most 'popular' tweets.
    counter = 0
    for k in sorted(response_dict, key=lambda k: 0 if (not k['tweet_volume']) else (k['tweet_volume']), reverse=True):
        if counter < 10:
            print k
        counter += 1


if __name__ == "__main__":
    main()
