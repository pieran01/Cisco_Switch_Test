#Set up logging for Cisco Switch Test

import logging
import logging.handlers
from listbox_logger_class import LISTBOXHandler


log = logging.getLogger("name")
log.setLevel(logging.DEBUG)

hand = logging.StreamHandler()
hand.setLevel(logging.DEBUG)

lhand = LISTBOXHandler()
lhand.setLevel(logging.INFO)

stream_format = logging.Formatter(fmt='%(asctime)s: %(filename).8s (%(levelname)s)\t- %(message)s',
                              datefmt='%d/%m/%Y %H:%M:%S')
hand.setFormatter(stream_format)

log.addHandler(hand)
log.addHandler(lhand)

log.debug("logsetup: Logging Started...")
log.info("logsetup: Info")


def setListBoxHandlerVar(strvar):
    lhand.listbox_var = strvar
    return

def setListBoxHandlerLines(no_of_lines):
    lhand.listbox_lines = no_of_lines
    return
