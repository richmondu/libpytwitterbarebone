###############################################################################
# Communicate with Twitter using Python-Twitter library
# pip install python-twitter
###############################################################################
import twitter
from twitter_credentials import twitter_credentials

import argparse
import sys



###############################################################################
CONFIG_TWITTER_CONSUMER_API_KEY    = twitter_credentials.CONSUMER_API_KEY
CONFIG_TWITTER_CONSUMER_SECRET_KEY = twitter_credentials.CONSUMER_SECRET_KEY
CONFIG_TWITTER_ACCESS_TOKEN        = twitter_credentials.ACCESS_TOKEN
CONFIG_TWITTER_ACCESS_SECRET       = twitter_credentials.ACCESS_SECRET
###############################################################################



def main(args):

#    logging.basicConfig(level=logging.DEBUG)

    message_to_send = "asdasdasd asdasdasd"

    api = twitter.Api(consumer_key=CONFIG_TWITTER_CONSUMER_API_KEY, 
        consumer_secret=CONFIG_TWITTER_CONSUMER_SECRET_KEY, 
        access_token_key=CONFIG_TWITTER_ACCESS_TOKEN, 
        access_token_secret=CONFIG_TWITTER_ACCESS_SECRET)
    print(api.VerifyCredentials()) 

    status = api.PostUpdate(message_to_send)
    print(status.text)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))


