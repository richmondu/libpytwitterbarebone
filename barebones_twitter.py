###############################################################################
# Communicate with Twitter using plain sockets and encryption library
###############################################################################
from twitter_credentials import twitter_credentials
import socket, ssl
import hashlib, hmac, base64, urllib.parse
import time, argparse, sys, random, string



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
CONFIG_TLS_CACERTIFICATE    = 'twitter_ca_cert.pem'
###############################################################################



class barebones_twitter:

    def __init__(self):
        self.session = None

    def getDateTimeStamps(self):
        timestamp = str(int(time.time()))
        print("\r\ntimestamp:\r\n{}\r\n".format(timestamp))
        return timestamp

    def generateRandom(self, num_chars):
        nonce = ''.join(random.choice(string.digits) for i in range(num_chars))
        print("\r\nnonce:\r\n{}\r\n".format(nonce))
        return nonce

    def generateSigningKey(self):
        signingkey = CONFIG_TWITTER_CONSUMER_SECRET_KEY + '&' + CONFIG_TWITTER_ACCESS_SECRET
        print("\r\nsigning key:\r\n{}\r\n".format(signingkey))
        
        return signingkey

    def percentEncode(self, data):
        data = urllib.parse.quote(data)
        data = data.replace("/", "%2F")
        return data

    def generateRequest(self, message_to_send):
        request = self.percentEncode(message_to_send)
        request = "status=" + request + "&trim_user=1"
        print("\r\nrequest:\r\n{}\r\n".format(request))
        return request

    def generateSignature(self, nonce, timeStamp, request):
        signing_key    = self.generateSigningKey()
        string_to_sign = self.generateStringToSign(nonce, timeStamp, request)

        signature = hmac.new(signing_key.encode("utf-8"), string_to_sign.encode('utf-8'), hashlib.sha1).hexdigest()
        print("\r\nHMACSHA1 signature:\r\n{}\r\n".format(signature))

        signature = hmac.new(signing_key.encode("utf-8"), string_to_sign.encode('utf-8'), hashlib.sha1).digest()
        signature = base64.b64encode(signature)
        print("\r\nBASE64 signature:\r\n{}\r\n".format(signature))

        signature = signature.decode("utf-8")
        signature = self.percentEncode(signature)
        print("\r\nsignature:\r\n{}\r\n".format(signature))
        return signature

    def generateStringToSign(self, nonce, timeStamp, request):
        header = CONFIG_HTTP_METHOD + "&" + self.percentEncode("https://" + CONFIG_HOST + CONFIG_HTTP_API) + "&"
        #print(header)

        body =  "oauth_consumer_key="     + self.percentEncode(CONFIG_TWITTER_CONSUMER_API_KEY) + "&"
        body += "oauth_nonce="            + self.percentEncode(nonce)                           + "&"
        body += "oauth_signature_method=" + self.percentEncode(CONFIG_HTTP_OAUTH_ALGORITHM)     + "&"
        body += "oauth_timestamp="        + self.percentEncode(timeStamp)                       + "&"
        body += "oauth_token="            + self.percentEncode(CONFIG_TWITTER_ACCESS_TOKEN)     + "&"
        body += "oauth_version="          + self.percentEncode(CONFIG_HTTP_OAUTH_VERSION)       + "&"
        body += request
        body = self.percentEncode(body)
        #print(body)

        data = header + body
        print("\r\nsignature base string:\r\n{}\r\n".format(data))
        return data

    def createRequestUpdate(self, message_to_send):
        request      = self.generateRequest(message_to_send)
        timeStamp    = self.getDateTimeStamps()
        nonce        = self.generateRandom(30)
        signature    = self.generateSignature(nonce, timeStamp, request)

        data = CONFIG_HTTP_METHOD + " " + CONFIG_HTTP_API + " " + CONFIG_HTTP_VERSION + "\r\n"
        #data += "Accept:"                  + CONFIG_HTTP_ACCEPT              + "\r\n"
        data += "Connection:"              + CONFIG_HTTP_CONNECTION          + "\r\n"
        data += "Content-Type:"            + CONFIG_HTTP_CONTENT_TYPE        + "\r\n"
        data += "Authorization:"           + CONFIG_HTTP_AUTHORIZATION       + ' '
        data += 'oauth_consumer_key="'     + CONFIG_TWITTER_CONSUMER_API_KEY + '",'
        data += 'oauth_nonce="'            + nonce                           + '",'
        data += 'oauth_signature="'        + signature                       + '",'
        data += 'oauth_signature_method="' + CONFIG_HTTP_OAUTH_ALGORITHM     + '",'
        data += 'oauth_timestamp="'        + str(timeStamp)                  + '",'
        data += 'oauth_token="'            + CONFIG_TWITTER_ACCESS_TOKEN     + '",'
        data += 'oauth_version="'          + '1.0"'                          + "\r\n"
        data += "Content-Length:"          + str(len(request))               + "\r\n"
        data += "Host:"                    + CONFIG_HOST                     + "\r\n"
        data += "\r\n"                     + request                         + "\r\n"

        print("\r\npacket:\r\n{}\r\n".format(data))
        return data

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
            return False
        return True

    def send(self, request):
        try:
            self.session.sendall(request.encode("utf-8"))
            #print("{} [{}]\r\n\r\n".format(request, len(request)))
        except:
            return False
        return True

    def recv(self):
        self.session.settimeout(1)
        bResult = True
        bFirst = True
        while True:
            try:
                response = self.session.recv(1024)
                if len(response) == 0:
                    break
                #print("{} [{}]".format(response, len(response)))
                if bFirst:
                    bFirst = False
                    response = response.decode("utf-8")
                    index = response.find("HTTP/1.1 200 OK")
                    if index < 0:
                        bResult = False
            except:
                bResult = False
                break
        #print("bResult={}\r\n".format(bResult))
        return bResult

    def close(self):
        self.session.close()


def tweet(message):
    result = False

    handle = barebones_twitter()
    request = handle.createRequestUpdate(message)
    if handle.connect(CONFIG_TLS_CACERTIFICATE):
        if handle.send(request):
            if handle.recv():
                result = True
        handle.close()

    print("Tweet sent {}! [{}] [{}]".format("successfully" if result else "failed", len(message), message))
    return result


def main(args):
    message = "asdasdasd asdasdasd"
    tweet(message)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
