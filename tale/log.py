import logging
import os

import graypy


FORMAT = '[%(asctime)s] [%(levelname)s] [PID: '+str(os.getpid())+'] [%(name)s]:  %(message)s'
formatter = logging.Formatter(FORMAT)

debug_handler = logging.FileHandler('debug.log')
debug_handler.setFormatter(formatter)

logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(debug_handler)


g_handler = graypy.GELFHandler('192.168.88.33', 13001)
g_handler.setFormatter(formatter)
logging.root.addHandler(g_handler)
