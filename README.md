# libpytwitterbarebone 


libpytwitterbarebone is a bare bone Python implementation of Twitter connectivity.
It uses plain sockets and encryption to send HTTP POST packet signed with OAuth signature and sent over secure TLS tunnel.

It is useful for people who want to know how to implement Twitter connectivity from scratch
without using Twitter libraries, such as the Python python-twitter library.


Supported Twitter features:

    1. Posting a tweet


Instructions:

    1. Create a Twitter developer account at https://developer.twitter.com
    2. Create an app.
    3. Copy the keys and tokens: (Used for generating OAuth signature)
       Consumer API keys
           API key
           API secret key
       Access token & access token secret:
           Access token
           Access token secret
    4. Update twitter_credentials.py

