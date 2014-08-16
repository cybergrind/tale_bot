import uuid
import json
import os
from urllib.request import urlopen, Request
from urllib.parse import urlencode


from tale.settings import CREDS, SESSION_FILE


URL = 'http://the-tale.org'

class Game(object):
    def __init__(self):
        self.connected = False
        self.private = {}
        self.init()

    def init(self):
        self.login()

    def login(self):
        if os.path.exists(SESSION_FILE):
            self.private = json.load(open(SESSION_FILE))
        if self.private.haskey('sessionid'):
            self.check_sessionid()
        url = '%s/accounts/auth/api/login?api_version=1.0&api_client=tb-test'%URL
        self.post(url, CREDS)

    def check_sessionid(self):
        pass

    def post(self, url, data):
        csrf = str(uuid.uuid4()).replace('-', '')
        post_data = urlencode(data).encode('utf8')
        print(post_data)
        r = Request(url)
        r.add_header('Cookie',
                     'csrftoken=%s;sessionid=%s'\
                     %(csrf, self.private['sessionid']))
        r.add_header('X-CSRFToken', csrf)
        uo = urlopen(r, post_data)
        print(dir(uo))
        print(uo.getheaders())
        j = uo.read().decode('utf8')
        print(j)
        j = json.loads(j)
        print(j['error'])
        

def main():
    Game()

if __name__ == '__main__':
    main()
