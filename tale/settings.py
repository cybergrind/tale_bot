
MIN_PERCENT = 1 - 0.0179*17

# minimal amount for building
BUILD_ENERGY_MIN = 8
PLAYER_ENERGY_MIN = 10

LEG_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-4'
EPC_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-3'
RAR_URL = 'http://the-tale.org/market/?order_by=0&group=cards-hero-good-2'

SHOP_LIMITS = {
    LEG_URL: 90,
    EPC_URL: 60,
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
