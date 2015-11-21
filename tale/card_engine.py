import logging
import json
import os
from functools import reduce

from tale.settings import DESIRED_CARDS


ITEMS = {
    0: {'name': 'рог изобилия',},
    1: {'name': 'озарение',},
    5: {'name': 'капля энергии',},
    6: {'name': 'чаша Силы',},
    7: {'name': 'магический вихрь',},
    8: {'name': 'энергетический шторм',},
    9: {'name': 'шквал Силы',},
    10: {'name': 'горсть монет',},
    11: {'name': 'увесистый кошель',},
    12: {'name': 'сундучок на счастье',},
    13: {'name': 'умеренность',},
    14: {'name': 'чревоугодие',},
    15: {'name': 'спокойствие',},
    16: {'name': 'вспыльчивость',},
    17: {'name': 'верность',},
    18: {'name': 'блуд',},
    19: {'name': 'дружелюбие',},
    20: {'name': 'алчность',},
    21: {'name': 'скромность',},
    22: {'name': 'тщеславие',},
    23: {'name': 'сдержанность',},
    24: {'name': 'гнев',},
    25: {'name': 'смирение',},
    26: {'name': 'гордыня',},
    27: {'name': 'миролюбие',},
    28: {'name': 'ярость',},
    29: {'name': 'знание врага',},
    30: {'name': 'новая родина',},
    31: {'name': 'новый соратник',},
    32: {'name': 'новый противник',},
    33: {'name': 'прозрение',},
    34: {'name': 'вкусы в экипировке',},
    35: {'name': 'определение лихости',},
    36: {'name': 'наскучившая вещь',},
    37: {'name': 'пересмотр стиля боя',},
    38: {'name': 'пересмотр ценностей',},
    39: {'name': 'альтернатива',},
    40: {'name': 'странный зуд',},
    41: {'name': 'магазинный импульс',},
    42: {'name': 'стремление к совершенству',},
    43: {'name': 'тяга к знаниям',},
    44: {'name': 'забота об имуществе',},
    45: {'name': 'фея-мастерица',},
    46: {'name': 'благословение Великого Творца',},
    47: {'name': 'другие заботы',},
    48: {'name': 'внезапная находка',},
    49: {'name': 'полезный подарок',},
    50: {'name': 'редкое приобретение',},
    51: {'name': 'дар Хранителя',},
    52: {'name': 'длань Смерти',},
    53: {'name': 'неразменная монета',},
    54: {'name': 'волшебный горшочек',},
    55: {'name': 'скатерть самобранка',},
    56: {'name': 'несметные богатства',},
    57: {'name': 'волшебный инструмент',},
    58: {'name': 'удачный день',},
    59: {'name': 'нежданная выгода',},
    60: {'name': 'удачная афёра',},
    61: {'name': 'преступление века',},
    62: {'name': 'погожие деньки',},
    63: {'name': 'торговый день',},
    64: {'name': 'городской праздник',},
    65: {'name': 'экономический рост',},
    66: {'name': 'ужасная погода',},
    67: {'name': 'запустение',},
    68: {'name': 'нашествие крыс',},
    69: {'name': 'экономический спад',},
    70: {'name': 'ошибка в архивах',},
    71: {'name': 'фальшивые рекомендации',},
    72: {'name': 'застолье в Совете',},
    73: {'name': 'интриги',},
    74: {'name': 'удачная мысль',},
    75: {'name': 'чистый разум',},
    76: {'name': 'неожиданные осложнения',},
    77: {'name': 'слово Гзанзара',},
    78: {'name': 'новые обстоятельства',},
    79: {'name': 'специальная операция',},
    80: {'name': 'слово Дабнглана',},
    81: {'name': 'благословение Дабнглана',},
    82: {'name': 'телепорт',},
    83: {'name': 'ТАРДИС',},
    84: {'name': 'амнезия',},
    85: {'name': 'донор Силы',},
    86: {'name': 'взыскание долга',},
    87: {'name': 'ритуал Силы',},
    88: {'name': 'волшебное точило',},
    89: {'name': 'суть вещей',},
    90: {'name': 'обычный спутник',},
    91: {'name': 'необычный спутник',},
    92: {'name': 'редкий спутник',},
    93: {'name': 'эпический спутник',},
    94: {'name': 'легендарный спутник',},
    95: {'name': 'новый взгляд',},
    96: {'name': 'чуткость',},
    97: {'name': 'благословение Гзанзара',},
    98: {'name': 'новый путь',},
    99: {'name': 'четыре стороны',},
    100: {'name': 'передышка',},
    101: {'name': 'подорожник',},
    102: {'name': 'священный мёд',},
    103: {'name': 'молодильное яблоко',},
    104: {'name': 'живая вода',},
    105: {'name': 'забота о ближнем',},
    106: {'name': 'скрытый потенциал',},
    107: {'name': 'туз в рукаве',},
    108: {'name': 'улыбка фортуны',},
    109: {'name': 'выгодный контракт',},
    110: {'name': 'сорванный контракт',},
}

FILE = 'items.json'
MAX_COMBINE = 3


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
            if not self.items[t].get('rarity'):
                v = self.items[t]
                v['rarity'] = card['rarity']
                self.update_items(t, v)

    def reduce_filter(self, acc, card):
        self.log.debug('Check card: {!r} {!r}'.format(card, acc))
        if card['type'] in DESIRED_CARDS:
            return acc
        r = card['rarity']
        if r > MAX_COMBINE:
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
            if len(uids) > 2:
                self.api.combine_cards(uids[:3])

    def update(self, cards):
        self.cards = cards
        self.update_cards_info()
        self.card_ready = cards['help_count'] > cards['help_barrier']
        self.check_combine()
        self.check_get_card()

    # {'cards': [{'auction': False, 'rarity': 4, 'type': 94, 'uid': 45, },
    #            {'auction': True, 'rarity': 2, 'type': 92, 'uid': 311}
