
MIN_PERCENT = 1 - 0.0179*17

# minimal amount for building
BUILD_ENERGY_MIN = 8
PLAYER_ENERGY_MIN = 10
CARD_FARMING_MIN = 8000
HELP_IN_BATTLE = False
MAX_HELPS_IN_ROW = 6

DESIRED_CARDS = {
    1: {'rarity': 4},  # + level
    8: {'rarity': 3},  # + energy 640
    9: {'rarity': 4},  # + energy 2560
    46: {'rarity': 3},  # + fix all arts
    50: {'rarity': 2},  # rare item
    97: {'rarity': 4},  # + experience
    106: {'rarity': 3},  # item enchance
    107: {'rarity': 4},  # + city help
    92: {'rarity': 2},  # + companion
    93: {'rarity': 3},  # + compoanion
    94: {'rarity': 4},  # + compoanion
    98: {'rarity': 1},  # reset all skills
    49: {'rarity': 1},  # + item
}

LEG_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-4'
EPC_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-3'
RAR_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-2'

SHOP_LIMITS = {
    LEG_URL: 85,
    EPC_URL: 55,
    RAR_URL: 20,
}

URL = 'http://the-tale.org'
BUILDINGS = ['x=31&y=46',
             'x=33&y=46']



def xfile(afile, globalz=None, localz=None):
    with open(afile, "r") as fh:
        exec(fh.read(), globalz, localz)

try:
    xfile('settings_local.py', globals(), locals())
except Exception as mess:
    print(mess)

import tale.log
