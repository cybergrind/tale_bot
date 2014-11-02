import logging
import os


FORMAT = '[%(asctime)s] [%(levelname)s] [PID: '+str(os.getpid())+'] [%(name)s]:  %(message)s'
formatter = logging.Formatter(FORMAT)

debug_handler = logging.FileHandler('debug.log')
debug_handler.setFormatter(formatter)

logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(debug_handler)
