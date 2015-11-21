import uuid
import json
import os
import re
import time
import logging
import sys
from bs4 import BeautifulSoup as bs


from urllib.request import urlopen, Request
from urllib.parse import urlencode

from tale.card_engine import CardEngine
from tale.settings import (CREDS, SESSION_FILE, MIN_PERCENT,
                           BUILD_ENERGY_MIN, PLAYER_ENERGY_MIN,
                           SHOP_LIMITS, URL, BUILDINGS, CARD_FARMING_MIN)


class Game(object):
    log = logging.getLogger('Game')

    def __init__(self):
        self.connected = False
        self.private = {'sessionid': ''}
        self.log.info(sys.argv)
        if len(sys.argv) >= 2 and sys.argv[1] == 'buy':
            self.buy_mode = True
        else:
            self.buy_mode = False
        self.card_engine = CardEngine(api=self)
        self.log.info('Buy mode is enabled: {}'.format(self.buy_mode))
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
                self.check_player_help()
                if self.buy_mode:
                    self.check_buy()
            except Exception as e:
                print('Got exception: {}'.format(e))
            finally:
                time.sleep(60)

    def check_buy(self):
        for url, limit in SHOP_LIMITS.items():
            self.check_section(url, limit)

    def check_section(self, url, limit):
        r = bs(self.get(url), 'lxml')
        tr = r.find_all(id='pgf-help-accordion')[0].table.tbody.tr
        card, price, lnk = self.check_price(tr)
        if price < limit:
            self.log.info('Buy card: {}'.format(card))
            s = self.post(lnk, {})
            self.log.info('Ret: {}'.format(s))
        else:
            self.log.info('No cards with available limits')

    def check_price(self, tr):
        desc = tr.td.span.text.strip()
        ps = tr.td.next_sibling.next_sibling
        p = int(ps.string.strip())
        a = ps.next_sibling.next_sibling.next_sibling.next_sibling.a['href']
        a = '{}{}'.format(URL, a)
        self.log.info('{} => {}'.format(desc, p))
        return (desc, p, a)

    def check_if_death(self):
        resp = self.get_info()
        # print('Energy: {}'.format(self.energy))
        # print('IS ALIVE: {}'.format(self.is_alive))
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

        durabilities = list(filter(lambda x: x[0] < MIN_PERCENT,
                                   map(self.get_durability, BUILDINGS)))
        durabilities.sort()
        self.log.debug('Sorted: {}'.format(durabilities))
        for building in durabilities:
            dur, bid, coord = self.get_durability(building[2])
            self.log.debug('Integrity: {} BID: {}'.format(dur, bid))
            if dur >= MIN_PERCENT:
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

    def check_player_help(self):
        self.get_info()
        if self.energy_bonus > CARD_FARMING_MIN:
            num = min(4, (CARD_FARMING_MIN-self.energy)/4)
            for i in range(num):
                self.player_help(fast=True)

        if self.energy < PLAYER_ENERGY_MIN:
            return
        self.player_help()

    def player_help(self, fast=False):
        pat = '{}/game/abilities/help/api/use?{}'
        url = pat.format(URL, self.vsn(1.0))
        self.log.debug('Player help')
        resp = self.post(url, {})
        self.log.info('Player help {}'.format(resp))
        time.sleep(3 if fast else 30)
        self.get_info()

    def get_card(self):
        # class='pgf-get-card-button'
        # POST: http://the-tale.org/game/cards/api/get?api_client=the_tale-v0.3.20.2&api_version=1.0
        pat = '{}/game/cards/api/get?{}'
        url = pat.format(URL, self.vsn(1.0))
        self.log.debug('Before get card')
        resp = self.post(url, {})
        self.log.debug('Get card resp: {}'.format(resp))

    def combine_cards(self, ids):
        # /game/cards/api/combine?api_client=the_tale-v0.3.20.2&api_version=1.0&cards=369,370,352
        pat = '{}/game/cards/api/combine?{}'
        ids = ','.join(map(str, ids))
        url = pat.format(URL, self.vsn(1.0, {'cards': ids}))
        self.log.debug('Before combine cards: {}'.format(ids))
        resp = self.post(url, {})
        self.log.debug('Combine cards resp: {}'.format(resp))

    def fix_building(self, bid):
        pat = '{}/game/abilities/building_repair/api/use?building={}&{}'
        url = pat.format(URL, bid, self.vsn(1.0))
        self.log.debug('POST: {}'.format(url))
        resp = self.post(url, {})
        self.log.info('Building fix resp: {}'.format(resp))
        time.sleep(30)  # async op dirty hack
        self.get_info()

    def get_durability(self, coord):
        self.log.debug('try durability')
        url = '{}/game/map/cell-info?{}'.format(URL, coord)
        resp = self.get(url)
        # self.log.debug('Get resp: {}'.format(resp))
        # regex = '.*data-building-integrity="(.*?)".*'
        regex = '.*"pgf-building-integrity"\>(.*?)%\<.*'
        integrity = re.match(regex, resp, re.DOTALL).groups()[0]
        regex = '.*data-building-id="(.*?)".*'
        bid = re.match(regex, resp, re.DOTALL).groups()[0]
        self.log.debug('Int: {}'.format(integrity))
        return (float(integrity), int(bid), coord)

    def login(self):
        url = '{}/accounts/auth/api/login?{}'.format(URL, self.vsn(1.0))
        resp, headers = self.post(url, CREDS, return_headers=True)
        cookie = list(filter(lambda x: x[0] == 'Set-Cookie', headers))[1][1]
        self.log.info('Cookie {} \nResp {}'.format(cookie, resp))
        self.private['sessionid'] = re.match('sessionid=(.*?);.*', cookie).groups()[0]
        self.private.update(resp['data'])
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.private, f)

    def get_info(self):
        url = '{}/game/api/info?{}'.format(URL, self.vsn(1.3))
        resp = self.get(url)
        hero = resp['data']['account']['hero']
        self.hero = hero
        self.energy = hero['energy']['value']
        self.energy_bonus = hero['energy']['bonus']
        self.is_alive = hero['base']['alive']
        self.card_engine.update(hero['cards'])
        self.log.debug('Hero info: {}'.format(hero))
        return resp

    def vsn(self, v, additional={}):
        opts = {'api_version': v,
                'api_client': 'tb-test'}
        if additional:
            opts.update(additional)
        return urlencode(opts)

    def check_sessionid(self):
        self.log.info('Check session')
        self.get_info()

    def post(self, url, data, return_headers=False):
        csrf = str(uuid.uuid4()).replace('-', '')
        post_data = urlencode(data).encode('utf8')
        # print(post_data)
        r = Request(url)
        r.add_header('Cookie',
                     'csrftoken=%s;sessionid=%s'
                     % (csrf, self.private['sessionid']))
        r.add_header('X-CSRFToken', csrf)
        uo = urlopen(r, post_data, timeout=30)
        # print(dir(uo))
        # print(uo.getheaders())
        j = uo.read().decode('utf8')
        # print(j)
        j = json.loads(j)
        if return_headers:
            return (j, uo.getheaders())
        else:
            return j

    def get(self, url, return_headers=False):
        csrf = str(uuid.uuid4()).replace('-', '')
        r = Request(url)
        r.add_header('Cookie',
                     'csrftoken=%s;sessionid=%s'
                     % (csrf, self.private['sessionid']))
        r.add_header('X-CSRFToken', csrf)
        uo = urlopen(r, timeout=30)
        # print(dir(uo))
        # print(uo.getheaders())
        j = uo.read().decode('utf8')
        # print(j)
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
