MIN_PERCENT = 1 - 0.0179*17

# minimal amount for building
BUILD_ENERGY_MIN = 8
PLAYER_ENERGY_MIN = 10
HELP_IN_BATTLE = False
MAX_HELPS_IN_ROW = 6

CARD_FARMING_MIN = 10000
CARD_ROLL_RATE = 0.03  # if proc: combine 2 instead of 3 cards
CARD_ROLL_LEVELS = [1, 2, 3]  # we want rares
DESIRED_CARDS = {
    1: {'rarity': 4},  # + level
    5: {'rarity': 0},  # + energy 10
    6: {'rarity': 1},  # + energy 40
    7: {'rarity': 2},  # + energy 160
    8: {'rarity': 3},  # + energy 640
    9: {'rarity': 4},  # + energy 2560

    30: {'rarity': 1},  # new fav town
    31: {'rarity': 1},  # new friend
    32: {'rarity': 1},  # new foe
    36: {'rarity': 1},  # new fav item

    46: {'rarity': 3},  # + fix all arts
    49: {'rarity': 1},  # + item
    50: {'rarity': 2},  # rare item
    106: {'rarity': 3},  # item enchance

    97: {'rarity': 4},  # + experience

    107: {'rarity': 4},  # + city help
    92: {'rarity': 2},  # + companion
    93: {'rarity': 3},  # + companion
    94: {'rarity': 4},  # + companion
    98: {'rarity': 1},  # reset all skills
    87: {'rarity': 4},  # exp to energy

    110: {'rarity': 0},  # town -1%
    66: {'rarity': 1},  # -4%
    67: {'rarity': 2},  # -16%
    68: {'rarity': 3},  # -64%
    69: {'rarity': 4},  # -256%

    70: {'rarity': 1},  # help +1
    71: {'rarity': 2},  # +4
    72: {'rarity': 3},  # +16
    73: {'rarity': 4},  # +64

}
AUTOUSE_CARDS = [1, 5, 6, 7, 8, 9]

LEG_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-4'
EPC_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-3'
RAR_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-2'

SHOP_LIMITS = {
    LEG_URL: 85,
    EPC_URL: 45,
    RAR_URL: 15,
}

URL = 'http://the-tale.org'
BUILDINGS = ['x=31&y=46']



def xfile(afile, globalz=None, localz=None):
    with open(afile, "r") as fh:
        exec(fh.read(), globalz, localz)

try:
    xfile('settings_local.py', globals(), locals())
except Exception as mess:
    print(mess)

import tale.log
