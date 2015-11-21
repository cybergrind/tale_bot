import logging
import json
import random
import os
from functools import reduce

from tale.settings import (DESIRED_CARDS, CARD_ROLL_RATE, CARD_ROLL_LEVELS)
from tale.items import ITEMS


FILE = 'items.json'
MAX_COMBINE_RARITY = 3

NEED_FOR_ROLL = 2
NEED_FOR_COMBINE = 3


class CardEngine(object):
    log = logging.getLogger('CardEngine')

    def __init__(self, api):
        self.api = api
        if os.path.exists(FILE):
            self.items = {int(x[0]): x[1] for x in json.loads(open(FILE).read()).items()}
        else:
            self.items = ITEMS
            self.save_items()

    def update_items(self, k, v):
        self.log.debug('Update {} => {}'.format(k, v))
        self.items[k] = v
        self.save_items()

    def save_items(self):
        i = json.dumps({str(x[0]): x[1] for x in self.items.items()})
        with open(FILE, 'w') as f:
            f.write(i)

    def check_get_card(self):
        if self.card_ready:
            self.api.get_card()

    def update_cards_info(self):
        for card in self.cards['cards']:
            t = card['type']
            if t not in self.items:
                v = {'rarity': card['rarity'], 'name': card['name']}
                self.log.info('Add not tracked card: {}'.format(card))
                self.update_items(t, v)
            elif not self.items[t].get('rarity'):
                v = self.items[t]
                v['rarity'] = card['rarity']
                self.update_items(t, v)

    def reduce_filter(self, acc, card):
        self.log.debug('Check card: {!r} {!r}'.format(card, acc))
        if card['type'] in DESIRED_CARDS:
            return acc
        r = card['rarity']
        if r >= MAX_COMBINE_RARITY:
            return acc
        if r not in acc:
            acc[r] = []
        acc[r].append(card['uid'])
        return acc

    def check_combine(self):
        self.log.debug('Cards: {}'.format(self.cards['cards']))
        by_lvl = reduce(self.reduce_filter, self.cards['cards'], {})
        self.log.debug('BY LEVEL: {}'.format(by_lvl))
        for lvl, uids in by_lvl.items():
            if len(uids) < NEED_FOR_COMBINE:
                continue

            if (lvl in CARD_ROLL_LEVELS and random.random() < CARD_ROLL_RATE):
                self.log.info('Roll new card of level {}'.format(lvl))
                self.api.combind_cards(uids[:NEED_FOR_ROLL])
            else:
                self.log.info('Roll card of new level {}+1'.format(lvl))
                self.api.combine_cards(uids[:NEED_FOR_COMBINE])

    def update(self, cards):
        self.cards = cards
        self.update_cards_info()
        self.card_ready = cards['help_count'] >= cards['help_barrier']
        self.check_combine()
        self.check_get_card()

    # {'cards': [{'auction': False, 'rarity': 4, 'type': 94, 'uid': 45, },
    #            {'auction': True, 'rarity': 2, 'type': 92, 'uid': 311}
