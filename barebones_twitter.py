###############################################################################
# Communicate with Twitter using plain sockets and encryption library
###############################################################################
import socket, ssl
import hashlib, hmac
import datetime
from twitter_credentials import twitter_credentials

import argparse
import sys
import urllib.parse
import time
import random
import string
import base64
import logging



###############################################################################
CONFIG_TWITTER_CONSUMER_API_KEY    = twitter_credentials.CONSUMER_API_KEY
CONFIG_TWITTER_CONSUMER_SECRET_KEY = twitter_credentials.CONSUMER_SECRET_KEY
CONFIG_TWITTER_ACCESS_TOKEN        = twitter_credentials.ACCESS_TOKEN
CONFIG_TWITTER_ACCESS_SECRET       = twitter_credentials.ACCESS_SECRET
###############################################################################
CONFIG_HTTP_METHOD          = 'POST'
CONFIG_HTTP_API             = '/1.1/statuses/update.json'
CONFIG_HTTP_VERSION         = 'HTTP/1.1'
CONFIG_HTTP_ACCEPT          = '*/*'
CONFIG_HTTP_CONNECTION      = 'close'
CONFIG_HTTP_CONTENT_TYPE    = 'application/x-www-form-urlencoded'
CONFIG_HTTP_AUTHORIZATION   = 'OAuth'
CONFIG_HTTP_OAUTH_ALGORITHM = 'HMAC-SHA1'
CONFIG_HTTP_OAUTH_VERSION   = '1.0'
CONFIG_HOST                 = 'api.twitter.com'
CONFIG_PORT                 = 443
CONFIG_MAX_RECV_SIZE        = 512
###############################################################################



class mytwitter:
    def __init__(self):
        self.session = None

    def getDateTimeStamps(self):
        timestamp = str(int(time.time()))
        print(timestamp)
        return timestamp

    def generateRandom(self, num_chars):
        nonce = ''.join(random.choice(string.digits) for i in range(num_chars))
        print(nonce)
        return nonce

    def generateSigningKey(self):
        key = CONFIG_TWITTER_CONSUMER_SECRET_KEY + '&' + CONFIG_TWITTER_ACCESS_SECRET
        print(key)
        return key

    def connect(self, ca_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_verify_locations(ca_file)
        self.session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.session = context.wrap_socket(self.session, server_hostname=CONFIG_HOST)
        
        server = socket.getaddrinfo(CONFIG_HOST, CONFIG_PORT)[0][-1]
        try:
            self.session.connect(server)
        except:
            print("Error: could not connect to server. Please check if server is running!")
            self.session.close()
            self.session = None

    def percentEncode(self, data):
        data = urllib.parse.quote(data)
        data = data.replace("/", "%2F")
        return data

    def generateRequest(self, message_to_send):
        request = self.percentEncode(message_to_send)
        request = "status=" + request
        request.encode("utf-8")
        return request

    def generateSignature(self, signing_key, string_to_sign):
        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha1).digest()
        #print(signature)
        signature = base64.b64encode(signature)
        signature = signature.decode("utf-8")
        signature = self.percentEncode(signature)
        print(signature)
        return signature

    def generateStringToSign(self, nonce, timeStamp, message_to_send):
        url = "https://" + CONFIG_HOST + CONFIG_HTTP_API
        header = CONFIG_HTTP_METHOD + "&" + self.percentEncode(url) + "&"
        header = header.replace("/", "%2F")
        #print(header)

        data = ""
        data += "oauth_consumer_key=" + self.percentEncode(CONFIG_TWITTER_CONSUMER_API_KEY)   + "&"
        data += "oauth_nonce=" + self.percentEncode(nonce)                                  + "&"
        data += "oauth_signature_method=" + self.percentEncode(CONFIG_HTTP_OAUTH_ALGORITHM) + "&"
        data += "oauth_timestamp=" + self.percentEncode(timeStamp)                          + "&"
        data += "oauth_token=" + self.percentEncode(CONFIG_TWITTER_ACCESS_TOKEN)            + "&"
        data += "oauth_version=" + self.percentEncode(CONFIG_HTTP_OAUTH_VERSION)            + "&"
        data += "status=" + self.percentEncode(message_to_send)                             + "&"

        data += "trim_user=1"

        data = self.percentEncode(data)
        #print(data)
        data = header + data
        print("\r\nsignature base string:\r\n{}\r\n".format(data))
        return data

    def createRequest(self, message_to_send):

        request      = self.generateRequest(message_to_send)
        timeStamp    = self.getDateTimeStamps()
        nonce        = self.generateRandom(30)
        signingKey   = self.generateSigningKey()
        stringToSign = self.generateStringToSign(nonce, timeStamp, message_to_send)
        signature    = self.generateSignature(signingKey.encode("utf-8"), stringToSign)

        data = CONFIG_HTTP_METHOD + " " + CONFIG_HTTP_API + " " + CONFIG_HTTP_VERSION + "\r\n"
        data += "Accept:"                  + CONFIG_HTTP_ACCEPT              + "\r\n"
        data += "Connection:"              + CONFIG_HTTP_CONNECTION          + "\r\n"
        data += "Content-Type:"            + CONFIG_HTTP_CONTENT_TYPE        + "\r\n"
        data += "Authorization:"           + CONFIG_HTTP_AUTHORIZATION + ' '

        data += 'oauth_consumer_key="'     + CONFIG_TWITTER_CONSUMER_API_KEY + '", '
        data += 'oauth_nonce="'            + nonce                           + '", '
        data += 'oauth_signature="'        + signature                       + '", '
        data += 'oauth_signature_method="' + CONFIG_HTTP_OAUTH_ALGORITHM     + '", '
        data += 'oauth_timestamp="'        + str(timeStamp)                  + '", '
        data += 'oauth_token="'            + CONFIG_TWITTER_ACCESS_TOKEN     + '", '
        data += 'oauth_version="'          + '1.0"'                                 + "\r\n"

        request += "&trim_user=1"

        data += "Content-Length:" + str(len(request)) + "\r\n"
        data += "Host:" + CONFIG_HOST                 + "\r\n"
        data += "\r\n"

        data += request + '\r\n'

#        print(data)
        return data

    def sendRequest(self, request):
        self.session.sendall(request.encode("utf-8"))
        print("{} [{}]".format(request, len(request)))

    def recvResponse(self):
        self.session.settimeout(1)
        while True:
            try:
                response = self.session.recv(1024)
                if len(response) == 0:
                    break
                print("{} [{}]".format(response, len(response)))
            except:
                pass

    def close(self):
        self.session.close()


def main(args):

    message_to_send = "asdasdasd asdasdasd"

    tweet = mytwitter()
    request_input = tweet.createRequest(message_to_send)
    tweet.connect('twitter_ca_cert.pem')
    tweet.sendRequest(request_input)
    tweet.recvResponse()
    tweet.close()


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
