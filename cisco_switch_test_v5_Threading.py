#v2 to split check_fc_port into parts
#v5 tidy up outputs as 'print' statements will be redirected to GUI
#v5_Threading:
#   -add logging statements to output to display
#   add log_in checks to save_log 

import serial
import tkinter
import tkinter.messagebox
import sys
import time

import threading
lock = threading.RLock()
import logging
log = logging.getLogger("name")

#Open serial/com port
def open_serial_port(com_port):
    if not lock.acquire(False):
        log.debug("Can't run, another thread running...")
        return
    log.debug("opening serial port")
    global cisco
    #create serial communication:
    try:
        cisco = serial.Serial(com_port,9400, timeout=1)
        log.info("Comms's Opened")
    except Exception:
        if cisco.isOpen():
            log.info("Comm's already open")
            #Need to catch when the port is not connected to anything
            #since it still seems to open a port somehow.
            #Also check that chaning the com port attempts
            #to open on the new port
        else:
            log.info("unable to open port")
    log.debug("Open serial port function complete")
    lock.release()
    return

#---------taken from serial_example-------------------#
#Procedure to send message via serial port
def send(message=""):
    log.debug("Send message: " + message)
    if cisco.isOpen():
        message = message + "\r"
        cisco.write(message.encode())
        time.sleep(0.1)
        log.debug("Message Sent")
        return
    log.debug("Message not sent")
    return      #this return and last log message was added recently
                #if it don't work - delete here.

#Function to read the output from serial
def read():
    if cisco.isOpen():                            #check serial comms
        if cisco.inWaiting() > 0:                 #check there is something to read
            output = cisco.readlines()              #read it
            for x in range(0, len(output)):       #decode the output
                output[x] = output[x].decode().strip()
            return output                       #return what was read
        else:
            #print("nothing to read")
            return "nothing to read"

#Function to check an expected prompt is present
def find_prompt(prompt):
    log.debug("looking for prompt: " + prompt)
    if cisco.inWaiting() == 0:        #check a prompt is waiting to be read
        send("")                    #if not - send a CR to get a prompt
    output = read()                 #read anything waiting on the serial port
    log.debug("message received: " + output)    #TEMP - print the read
    last = output[len(output)-1]    #Locate the last line read
    log.debug("last message received = " + last)
    if last == prompt:              #check if last  line is prompt expected
        log.debug("prompt found")
        return True
    else:
        log.debug("not found")
        return False
#--------------------------------------------------------------#
    
#log in
def log_in():
    log.debug("CMD: running log_in")
    if not lock.acquire(False):
        log.debug("Can't run, another thread is running")
        return
    #check serial is open
    try:
        if cisco.isOpen() is False:
            log.warning("Unable to log in - not connected to switch")
            log.info("Attempting to connect to switch via serial...")
    except NameError:   #Serial not opened
            log.info("Serial Port not open. Opening now...")
            open_serial_port()
        

    if find_prompt("switch login:"):        #look for username prompt
        send("admin")                       #send username
        
        #assume that next prompt will be for password
        send("admin")       #send password

    #if not asking for login details - check if already logged in
    #as well as confirming that you have logged in
    if find_prompt("switch#"):
        log.info("you are now logged in")

    else:
        log.warning("Cannot login - check connected correctly")

    lock.release()
    return

#Function to show log length x and return it
def get_log(log_length=15):
    log.debug("Getting last " + str(log_length) + " entries of Cisco Log")
    #check serial is open
    try:
        if cisco.isOpen() is False:
            log.warning("Unable to log in - not connected to switch")
            log.info("Attempting to connect to switch via serial...")
    except NameError:   #Serial not opened
            log.info("Serial Port not open. Opening now...")
            open_serial_port()
     
    #Request the last 'log_length' number of entries of the log
    send("term len 0")
    message = "show log last " + str(log_length)
    send(message)
    output = read()  #response is expected to be a list of lines

    #print(output)   #for debug only
  
    #Check 'output' is something we expect:
    
    if output =="nothing to read":  #This is a string returned from read()
        log.warning("No response, check com port")
        return  False #No point carrying on

    if type(output) is not list:
        log.critical("Unexpected output")
        #find what outputs this could be and deal with them
        return False #Dont carry on

    return output


#confirm port X is up
def check_fc_port(port, log_length):
    log.debug("Checking if FC port " + str(port) + " is up")
    if not lock.acquire(False):
        log.debug("Can't run, another thread is running...")
        return
    c_log = get_log(log_length)

    #Confirm log is a list, if not there is some sort of error
    if type(c_log) is not list:
        log.warning("List not returned - cannot continue")
        lock.release()
        return
        

    #output is a list with index 0, which is 15 lines ago, and index 14
    #as the last line received.
    #Reverse this so that we can traverse the list
    #backwards (we want the latest 'port is up' otherwise a 'down' migh
    #have happened after)
    
    c_log.reverse() 

    port_up = "fc1/" + str(port) + " is up in mode F"
    port_down = "fc1/" + str(port) + " is down"

    #search through the output list to find port up and down statuses
    for i in range (0, len(c_log)):
        log.info(c_log[i])
        if port_down in c_log[i]:
            log.warning("Port " + str(port) + " is DOWN")
            return "down"

        if port_up in c_log[i]:
            log.info("port " + str(port) + " is UP")
            return "up"

    #if script gets this far port status was not found in the length
    #of log given. Add something to check further back in the log
    log.warning("Port status not found in last " + str(log_length) + " log entries.")
    log.warning("Check you are searching for the correct port")
    return "not found"

def check_fc_port_loop(port, log_length=25):
    if not lock.acquire(False):
        log.debug("Can't run, another thread is running...")
        return
    log.debug("CMD: check_fc_port_loop")
    status = check_fc_port(port, log_length)
    if status != "not found":
        lock.release()
        return status

    #Else status = "not found"
    log.debug("Status not found in last 25 entries.")
    log.debug("searching entire log...")
    status = check_fc_port(port, 1000)

    lock.release()
    return status #return what ever the result is after a log search.


#automate re-opening of port
def open_fc_port(port):
    log.debug("Re-opening FC port: " + str(port))
    if not lock.acquire(False):
        log.debug("Can't run, another thread is running...")
        return
    try:
        if cisco.isOpen() is False:
            log.warning("Unable to log in - not connected to switch")
            log.warning("Attempting to connect to switch via serial...")
    except NameError:   #Serial not opened
            log.info("Serial Port not open. Opening now...")
            open_serial_port()

    #print("Looking for normal prompt: switch#")
    if find_prompt("switch#") is False:
        #print("normal prompt not found - maybe already in conf mode:")
        if find_prompt("switch(config)#") is False:
            #print("not in conf mode either - maybe in conf int already:")
            if find_prompt("switch(config-if)#") is False:
                log.debug("unknown prompt - expected to be in config mode")
                lock.release()
                return

    #print("sending conf t")
    #Enter Configuration Mode
    send("conf t")

    #print("sending intfc1/port")  
    #Enter Interface Configuration Mode for selected port
    message = "int fc1/" + str(port)
    send(message)

    
    if find_prompt("switch(config-if)#") is False:
        log.warning("terminal received unexpected reply")
        lock.release()
        return

    log.debug("sending shutdown port")
    #Shutdown the port
    send("shutdown")

    if find_prompt("switch(config-if)#") is False:
        log.warning("unexpected response")
        lock.release()
        return

    log.debug("sending no shutdown")
    #Re-Open port
    send("no shutdown")
    
    if find_prompt("switch(config-if)#") is False:
        log.warning("unexpected response")
        lock.release()
        return

    #Exit Config mode
    #print("sending 1st exit")
    send("exit")    #exit config-if
    #print("sending 2nd exit")
    send("exit")    #exit config
    
    if find_prompt("switch#") is False:
        log.warning("terminal received unexpected reply")
        log.warning("expected normal prompt")
        lock.release()
        return

    #Check the port has been opened  
    if check_fc_port_loop(port) == "up":
        log.info("FC port " + str(port) + " has been re-opened")
    else:
        log.warning("FC port not opened.")
        log.warning("If a drive is not connected the port will not open")

    lock.release()
    return

#Save switch log to notepad for Results/putinhere
class get_out_of_loops(Exception):
    pass

def save_log(port, filepath):

    if not lock.acquire(False):
        log.debug("Can't run, another thread is running...")
        return
    log_in()    #Check you are logged into the switch

    port_up = "fc1/" + str(port) + " is up in mode F"   #string to find in log
    port_down = "fc1/" + str(port) + " is down"         #port down string
    up = False          #will be true if 'port up' found
    down = False        #will be true if port down found after a port up

    #great if port up is found, but what happens if the port is down
    #after the port up status? This will not look right in results - could
    #mean that the port closed during testing. Could also mean that the drive
    #was disconnected before the log was saved
    

    try:
        c_log = get_log(25)
        if c_log is False:
            log.warning("log not found - check connected")
            lock.release()
            return
        
        c_log.reverse()       #reverse the log
        for i in range(0, len(c_log)):
            if port_down in c_log[i]:
                log.warning("port down found before an up")
                down = True
                raise get_out_of_loops
            if port_up in c_log[i]:
                log.info("port up found in this log")
                up = True
                raise get_out_of_loops
            #else, status is still False

        #end of 'for loop', if status still not found:
        #search the entire log:

        c_log = get_log(1000)     #use big number to get entire log
                                #instead of sending show log log
        c_log.reverse()           #reverse the log
        for i in range(0, len(c_log)):
            if port_down in c_log[i]:
                log.warning("port down found before an up")
                down = True
                raise get_out_of_loops
            if port_up in c_log[i]:
                log.info("port up found in this log")
                up = True
                raise get_out_of_loops
            #else, status is still False
            
    except get_out_of_loops:
        pass
            
    if up is False and down is False:
        #port up not found in log
        #you could be looking for the
        #wrong port.
        log.warning("Port " + str(port) + " status not found in this log")
        log.warning("Check you are searching for the right port")
        log.warning("Not saving log as status not found")
        lock.release()
        return

    if up is False and down is True:
        log.warning("port DOWN status found after port up")
        log.warning("drive may have been disconnected before log saved")
        log.warning("or port closed but passed LTT")
        log.warning("not saving log as this shows a Failure")
        lock.release()
        return

    if up is True and down is False:
        #Port up status found for the searched port
        #save the log (what ever length was needed to get the status)
        log.info("Port UP status found")
        log.info("saving file...")

        #saving file:
        c_log.reverse() #write log so that last message is written last
        with open(filepath, 'w') as frank:
            for i in range(0, len(c_log)):
                frank.write(c_log[i] + "\n")

        log.info("saved")
        lock.release()
        return


#------------------------------------
#Main Calls to Program:

#open_serial_port()


#End
    

