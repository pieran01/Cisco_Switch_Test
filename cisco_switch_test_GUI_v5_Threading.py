#GUI for Cisco Switch Test
#v5 to display info returned from the function script:
#All buttons will required a link function to re-direct
#stdout to the display
#v5_Threading:
#   -remove 'redirection of stdout'
#   -insert logging for displaying messages to the screen
#   -turn functions into threads
#18/01/16

import sys
from io import StringIO
import threading
import time
import tkinter
from tkinter import messagebox
from tkinter import filedialog
import logging
import setup_logging                #small program to set up logging
log = logging.getLogger("name")     #get logger "name" to run in this module




#Main Tkinter Window Options:
top = tkinter.Tk()
top.geometry("600x200")
top.wm_title("Cisco Switch Test")

port = tkinter.IntVar()     #variable to hold the selected port
port.set(9)                 #set an initial value to '9'

com_port = tkinter.StringVar()       #variable to hold selected com port (serial comms)
com_port.set("COM1")                #set default value

var = tkinter.StringVar()                       #variable to hold the test to output to screen
var.set("Cisco Switch Test Initial Screen")     #set an initial value

setup_logging.setListBoxHandlerVar(var)         #give logger strvar 'var' for listbox
setup_logging.setListBoxHandlerLines(15)
log.debug("GUI: Logging initialised")
log.info("GUI: Logging initialised")

from cisco_switch_test_v5_Threading import open_serial_port
from cisco_switch_test_v5_Threading import log_in
from cisco_switch_test_v5_Threading import check_fc_port_loop
from cisco_switch_test_v5_Threading import open_fc_port
from cisco_switch_test_v5_Threading import save_log

#---------------------
#Commands go here:

#Most commands are imported from cisco_switch_test.py


def link_a():
    log.debug("GUI: link_a clicked")
    log.debug("GUI: com port '" + com_port.get() + "' selected")
    thread_a = threading.Thread(target=open_serial_port(com_port.get()))
    thread_a.start()    
    return

def link_b():
    log.debug("GUI: link_b clicked")
    thread_b = threading.Thread(target=log_in)
    thread_b.start()
           
    return

def link_c():
    log.debug("GUI: link_c clicked")
    thread_c = threading.Thread(target=check_fc_port_loop(port.get()))
    thread_c.start()

    return

def link_d():
    log.debug("GUI: link_d clicked")
    log.warning("Confirm Port...")
    confirm_port = messagebox.askokcancel("Warning! Check port...",
                                          "Check you have the"
                           " correct port selected."
                           " Continuing with the wrong port "
                           "will interfere with other tests."
                           " Click OK to continue with port: "
                           + str(port.get()) + ".")
    if confirm_port:
        log.info("Port confirmed, continue...")
        thread_d = threading.Thread(target=open_fc_port(port.get()))
        thread_d.start()
    else:
        log.info("Canceled Opening Port")
 
    return

def link_f():
    log.debug("GUI: link_f clicked")
    #open file browser
    name = "cisco-" + str(port.get()) + "-log.txt"
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", 
                                            initialdir="R:/putinhere/",
                                            initialfile=name,
                                            title="Save log to...")

    log.debug("Saveing to: " + filepath)

    if filepath != "":
        thread_f = threading.Thread(target=save_log(port.get(),filepath))
        thread_f.start()
    else:
        log.info("Saving Canceled.")

    return


#---------------------
#Controls go here:

a = tkinter.Button(top, text = "Open Serial Port", command = link_a)
b = tkinter.Button(top, text = "Log in to Switch", command = link_b)
c = tkinter.Button(top, text = "Check Port Status", command = link_c)
d = tkinter.Button(top, text = "Open FC Port", command = link_d)

e = tkinter.OptionMenu(top, port, 1, 2, 7, 9, 11)

f = tkinter.Button(top, text = "Save Log", command = link_f)

m = tkinter.Menu(top)
m_setup = tkinter.Menu(m, tearoff=0)
m_setup.add_radiobutton(label="COM1", variable=com_port, value="COM1")
m_setup.add_radiobutton(label="COM2", variable=com_port, value="COM2")
m_setup.add_radiobutton(label="COM3", variable=com_port, value="COM3")
m_setup.add_radiobutton(label="COM4", variable=com_port, value="COM4")
m.add_cascade(label="Com Port", menu=m_setup)

#--------------------
#Design goes here:
a.place(height=100, width=100, x=0, y=0)
b.place(height=100, width=100, x=0, y=100)
c.place(height=100, width=100, x=100, y=0)
d.place(height=100, width=100, x=100, y=100)

e.place(anchor='w', x=225, y=50, height=30, width=75)

f.place(height=100, width=100, x=200, y=100)

l = tkinter.Label(top, text="Port Selection:").place(anchor='w', x=210, y=20)

o = tkinter.Message(top, textvariable=var, bg='white', justify='left', relief='sunk', anchor='w', width=300)
o.place(x=300, y=0, width=300, height=200)


#--------------------
#Other Functions here:



#--------------------
#Main Call to start everything:
top.config(menu=m)
top.mainloop()

