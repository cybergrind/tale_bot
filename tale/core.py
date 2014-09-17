import uuid
import json
import os
import re
import time
import logging


from itertools import cycle
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from tale.settings import CREDS, SESSION_FILE


URL = 'http://the-tale.org'
BUILDINGS = ['x=31&y=39',
             'x=33&y=39']

# minimal amount for building
BUILD_ENERGY_MIN = 8


class Game(object):
    log = logging.getLogger('Game')
    def __init__(self):
        self.connected = False
        self.private = {'sessionid': ''}
        self.init()

    def init(self):
        self.log.warn('W')
        if os.path.exists(SESSION_FILE):
            self.private = json.load(open(SESSION_FILE))
        self.log.info('Privat {}'.format(self.private))
        if self.private['sessionid']:
            self.check_sessionid()
        else:
            self.login()
        self.loop()

    def loop(self):
        while True:
            try:
                self.check_if_death()
                self.check_buildings()
            except Exception as e:
                print('Got exception: {}'.format(e))
            finally:
                time.sleep(60)

    def check_if_death(self):
        resp = self.get_info()
        #print('Energy: {}'.format(self.energy))
        #print('IS ALIVE: {}'.format(self.is_alive))
        if not self.is_alive:
            url = '{}/game/abilities/help/api/use?{}'.format(URL, self.vsn(1.0))
            resp = self.post(url, {})
            self.log.warning('Ressurect: {}'.format(resp))
            self.get_info()

    def check_buildings(self):
        self.get_info()
        if self.energy < BUILD_ENERGY_MIN:
            self.log.debug('Low energy: {}. Skip building fix'.format(self.energy))
            return

        durabilities = list(filter(lambda x: x[0] < 0.99, map(self.get_durability, BUILDINGS)))
        durabilities.sort()

        for building in durabilities:
            dur, bid = self.get_durability(building)
            self.log.debug('Integrity: {} BID: {}'.format(dur, bid))
            if dur >= 0.99:
                self.log.debug('Do recursive')
                self.check_buildings()
                self.log.debug('After recursive return')
                return
            else:
                self.fix_building(bid)
            if self.energy < BUILD_ENERGY_MIN:
                msg = 'Low energy: {}. Skip building fix'.format(self.energy)
                self.log.debug(msg)
                return

    def fix_building(self, bid):
        pat = '{}/game/abilities/building_repair/api/use?building={}&{}'
        url = pat.format(URL, bid, self.vsn(1.0))
        self.log.debug('POST: {}'.format(url))
        resp = self.post(url, {})
        self.log.info('Building fix resp: {}'.format(resp))
        time.sleep(30) # async op dirty hack
        self.get_info()

    def get_durability(self, coord):
        self.log.debug('try durability')
        url = '{}/game/map/cell-info?{}'.format(URL, coord)
        resp = self.get(url)
        regex = '.*data-building-integrity="(.*?)".*'
        integrity = re.match(regex, resp, re.DOTALL).groups()[0]
        regex = '.*data-building-id="(.*?)".*'
        bid = re.match(regex, resp, re.DOTALL).groups()[0]
        return (float(integrity), int(bid))


    def login(self):
        url = '{}/accounts/auth/api/login?{}'.format(URL, self.vsn(1.0))
        resp, headers = self.post(url, CREDS, return_headers=True)
        cookie = list(filter(lambda x: x[0]=='Set-Cookie', headers))[1][1]
        self.log.info('Cookie {} \nResp {}'.format(cookie, resp))
        self.private['sessionid'] = re.match('sessionid=(.*?);.*', cookie).groups()[0]
        self.private.update(resp['data'])
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.private, f)

    def get_info(self):
        url = '{}/game/api/info?{}'.format(URL, self.vsn(1.1))
        resp = self.get(url)
        self.energy = resp['data']['account']['hero']['energy']['value']
        self.is_alive = resp['data']['account']['hero']['base']['alive']
        return resp

    def vsn(self, v):
        return 'api_version={}&api_client=tb-test'.format(v)


    def check_sessionid(self):
        self.log.info('Check session')
        self.get_info()

    def post(self, url, data, return_headers=False):
        csrf = str(uuid.uuid4()).replace('-', '')
        post_data = urlencode(data).encode('utf8')
        #print(post_data)
        r = Request(url)
        r.add_header('Cookie',
                     'csrftoken=%s;sessionid=%s'\
                     %(csrf, self.private['sessionid']))
        r.add_header('X-CSRFToken', csrf)
        uo = urlopen(r, post_data)
        #print(dir(uo))
        #print(uo.getheaders())
        j = uo.read().decode('utf8')
        #print(j)
        j = json.loads(j)
        if return_headers:
            return (j, uo.getheaders())
        else:
            return j

    def get(self, url, return_headers=False):
        csrf = str(uuid.uuid4()).replace('-', '')
        r = Request(url)
        r.add_header('Cookie',
                     'csrftoken=%s;sessionid=%s'\
                     %(csrf, self.private['sessionid']))
        r.add_header('X-CSRFToken', csrf)
        uo = urlopen(r)
        #print(dir(uo))
        #print(uo.getheaders())
        j = uo.read().decode('utf8')
        #print(j)
        try:
            j = json.loads(j)
        except Exception:
            pass
        if return_headers:
            return (j, uo.getheaders())
        else:
            return j


def main():
    Game()

if __name__ == '__main__':
    main()
