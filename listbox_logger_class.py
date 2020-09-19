# A class that creates a handler to direct logged messages to a strVar
# which can be used to update a tkinter list box
# Creating the handler requires a strVar and a 'number of lines' to display
# in the list box.
#
# Example initialisation:
#
#   from listbox_logger_class import LISTBOXHandler     # import the class
#
#   log = logging.getLogger()                           # the log which will use the handle
#   log.addHandler(LISTBOXHandler(strVar, 10))          # add handler to logger
#
# Version1  ALP 11/01/16

import logging
import logging.handlers


class LISTBOXHandler(logging.Handler):
    def __init__(self, listbox_var=False, listbox_lines=0):
        logging.Handler.__init__(self)
        self.listbox_var = listbox_var
        self.hist = []  
        self.listbox_lines = listbox_lines

    def emit(self, record):
        #print(record)
        r = self.format(record)
        #add to list until list is 10 items long
        if len(self.hist) > self.listbox_lines:
            self.hist.pop(0)
        self.hist.append(r)
    
        #display in listbox
        rstr = ""
        for i in range(0, len(self.hist)):
            rstr = rstr + self.hist[i] + "\n"
            
        if self.listbox_var:
            self.listbox_var.set(rstr)
        else:
            print("No StringVar")
            print(rstr)
            
        




