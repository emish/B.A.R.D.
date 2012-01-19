# The BARD overlay

## System modules
import sys, socket, threading, getopt, os
## Local modules
import p_engine, rulesUpdate, rule_generator

## default values for globals
host, port = "localhost", 9999
p_ratio = 0.5
max_atoms = 10000
## 10hr work week. 1 day, 2 days. 1 week = 168hrs. 1 month = 720hrs.
frames = [10, 24, 48]#, 168, 720]
## The list of persistant atoms that await user decision and white filtering
p_atoms = []
## Filenames
white_file = "../lists/whitelist.txt"
black_file = "../lists/blacklist_bard.rules"
et_rules = "../lists/blacklist_et.rules"
dump_path = "../dump"
## Locks
list_lock = threading.Lock()
white_lock = threading.Lock()


## Implements basic client functions for connecting to server
# and recieving data in the form of a string
class Client:
    ## The constructor
    # @param host The host to connect to
    # @param port The port to connect on
    def __init__(self):
        self.host = host
        self.port = port 
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    ## Recieves data in the form of a string
    # @return data string
    def get_data(self):
        data = []
        while 1:
            d = self.conn.recv(1024)
            data.extend(d)
            if len(d) < 1024: break
        return "".join(data)
    
    ## Starts a connection to the server to see if it is up
    # @return errorcode 0 if everything is ok, 1 otherwise
    def connect_to_server(self):
        try:
            self.conn.connect((self.host, self.port))
            return 1
        except socket.error, e:
            print >>sys.stderr, "Can't connect to remote host", str(e)
            return 0


## Class that runs Pengine as a thread
class PengineThread(threading.Thread):
    ## The constructor
    # @param pengine The class isntance that will be running under 
    # this thread
    def __init__(self):
        threading.Thread.__init__(self)
        self.pengine = p_engine.Pengine(frames, max_atoms, dump_path, p_ratio)

    ## Runs pengine indefinitely
    def run(self):
        while True:
            list_lock.acquire()
            p_atoms.append(self.pengine.run())
            print "p_atoms length: ",
            print len(p_atoms)
            list_lock.release()

    
## Performs updates to local files based on server response
class FileUpdateThread(threading.Thread, Client):
    ## The constructor
    # @param host The host to connect to
    # @param port The port to connect to
    def __init__(self):
        threading.Thread.__init__(self)
        Client.__init__(self)

    ## Updates the local blacklist and whitelist files
    # @param serv_white The text version of the new file
    # @param serv_black The text version of the new file
    def update_files(self, serv_white, serv_black):
        white_lock.acquire()
        white_fp = file(white_file, 'w')
        black_fp = file(black_file, 'w')
        
        print >>white_fp, serv_white
        print >>black_fp, serv_black
        white_fp.close()
        black_fp.close()
        white_lock.release()
        
    ## Runs the thread indefinitely
    # @return err The error code
    def run(self):
        if not self.connect_to_server():
            return 1
        err = 0
        while True:
            try:
                self.conn.send('3') # Check for whitelist update
                serv_white = self.get_data()
                self.conn.send('4') # Check for blacklist update
                serv_black = self.get_data()
            except socket.error, e:
                print >>sys.stderr, "Got a socket error in update files thread: ", str(e)
                err = 1
                break
            except (EOFError, KeyboardInterrupt):
                err = 1
                break
            self.update_files(serv_white, serv_black)
            # Update ET rules
            rulesUpdate.update()
        self.conn.close()
        return err

                
## Thread that handles user input, and updates the server with said input
class UserInputServerPushThread(threading.Thread, Client):
    ## The constructor
    # @param p_atoms The list of persistant atoms being stored by Bard at the moment
    def __init__(self):
        threading.Thread.__init__(self)
        Client.__init__(self)
        self.p_atoms = p_atoms
        self.sid = 1000001
        self.rg = rule_generator.rule_generator("../lists", self.sid)


    ## Removes whitelisted atoms from the list of persistent atoms gotten from
    #  Pengine.
    def filterWhites(self):
        white_lock.acquire()
        whiteList = open(white_file, "r")
        wll = []
        for line in whiteList:
            if(line != "\n"):
                wll.append(self.stringToAtom(line))
        for index, atom in enumerate(self.p_atoms):
            for j in wll:
                if(p_engine.compareAtoms(atom,j)):
                    self.p_atoms.pop(index)
                    break
        white_lock.release()                    

    ## Converts a line from the white_file into an atom object
    #  @param line A line from the file that corresponds to a whitelisted atom
    #  @return The atom object created for comparison with new p_atoms
    def stringToAtom(self, line):
        print "stringtoAtom ", line
        temp = line.split()
        print "stringtoAtom ", temp
        a = p_engine.Pengine.Atom(temp[0],temp[1],temp[2], -1)
        return a

    ## Prompts user for input on each atom for addition to white or black list
    def getDecisions(self):
        self.b_list = []
        self.w_list = []
        print("Assign each persistent atom to the blacklist (b) or whitelist (w) after each prompt\n")
        for index, atom in enumerate(self.p_atoms):
            print "here!"
            i = raw_input("Atom: " + str(atom.dest_ip) + ", " + str(atom.dest_port) + ", " + str(atom.protocol) + "\n")
            print "here2!"
            while( i != 'b' and i != 'w'):
                i = raw_input("Input b or w\n")
            if(i == 'b'):
                self.b_list.append(atom)
            elif(i == 'w'):
                self.w_list.append(atom)
            self.p_atoms.pop(index)
            
    ## Updates the server's blacklist and whitelist
    # @return err The error code
    def updateServer(self):
        if not self.connect_to_server():
            return 1
        err = 0
        # Create snort rules
        b_list_rules = ""
        for b_atom in self.b_list:
            b_list_rules = b_list_rules + rg.block(b_atom) + "\n"
        w_list_str = ""
        for w_atom in self.w_list:
            w_list_str = a_list_str + w_atom + "\n"
        while True:
            try:                
                self.conn.send('1') # Prompt to update whitelist
                data = self.get_data()
                print data
                if data != "whitelist":
                    err = 1
                    break
                print "sending white list: ", '1' + w_list_str
                self.conn.send('1'+ w_list_str)
                if self.get_data() != 'ok':
                    err = 1
                    break
                self.conn.send('2') # Prompt to update blacklist
                if self.get_data() != 'blacklist':
                    err = 1
                    break
                self.conn.send(b_list_rules)
                if self.get_data() != 'ok':
                    err = 1
                    break
                break
            except socket.error, e:
                print >>sys.stderr, "Got a socket error in updateServer thread: ", str(e)
                err = 1
                break
            except (EOFError, KeyboardInterrupt):
                err = 1
                break
        self.conn.close()
        return err

    ## Runs the thread indefinitely
    def run(self):
        while True:
            x = raw_input("Press Enter to label atoms")
            self.filterWhites()
            self.getDecisions()
            print "Got Decisions"
            if self.updateServer() != 0:
                print "There was an error in Server update"
                return 1


                
## The overarching Bard Class. Handles all operations from a threaded
# standpoint.
# Calls: p_engine for packet analysis
# snort for packet sniffing and blocking
# parser for snort output parsing
# etc..
# @param host The host ip to host the program
# @param port The port to use for socket connections
class Bard(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        ## Initialize all components
        self.host = host
        self.port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    ## Begins by checking if the server is up
    def start(self):
        # start snort
        #os.system("sudo /usr/local/snort/bin/snort -c /usr/local/snort/etc/snort_inline.conf -Q --daq afpacket -i eth0:vmnet1::eth0:vmnet8 -b -l ../dump &")

        # start UserInputServerPushThread
        uisp = UserInputServerPushThread();
        uisp.start()

        # start PEngine thread
        pen = PengineThread();
        pen.start()
        
        # start FileUpdate thread
        fup = FileUpdateThread();
        fup.start()
        
        while 1: 
            user_input = "" #sys.stdin.readlines()
            if user_input == 'exit':
                #shut down threads
                sys.exit()
        
        
        
help_msg = """ Welcome to BARD. For help type --help.
Window size is hardcoded to 1hr. Please set frame to be a number of windows.
List of options:
-p --port to specify a port number
-h --host to specify a host ip
-t --threshold to specify a threshold persistence ration (between 0 and 1)
-f --frames to specify custom frame size. Must be comma delimited, no spaces. 
"""

## Usage() Exception is caught at the end of main(). 
# Provides main with a single exit point for graceful error handling
class Usage(BaseException):
    def __init__(self, msg):
        self.msg = msg

## The main method called on runtime
def main(argv=None):
    global port, host, p_ratio, frames, help_msg
    if argv is None:
            argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "p:h:t:f:d:", 
                                       ["help", "port", "host", "threshold",
                                        "frame", "debug"])
            for o, a in opts:
                print 'checking o,a'
                print o, a
                if o == '-p' or o == '--port':# ('-p', '--port'):
                    print 'got here'
                    a = int(a)
                    assert a > 0 and a <=65536, "Invalid Port"
                    port = a
                    print "Reassigned port"
                if o in ('-h', '--host'):
                    # could place ip check here
                    host = a
                if o in ('-t', '--threshold'):
                    assert a <= 1 and a > 0, "Invalid ratio, must be between 0 and 1"
                    p_ratio = a
                if o in ('-f', '--frame'):
                    a_parsed = a.split(',')
                    for x in a_parsed:
                        assert type(int(x)) == int, "Incorrect format of frame, must be int"
                        frames.append(int(x))
                if o in ('-d', '--debug'):
                    a_parsed = a.split(',')
                    "You picked atom list ", a_parsed
                if o == '--help':
                    print help_msg
                    return 0
        except AssertionError, msg:
            raise Usage(msg)
    except Usage, msg:
        print msg
        return 1
    
    # Start Program 
    x = Bard()
    x.start()
    # End Program
    print "Thank you for using BARD!"
    return 0

    
if __name__ == "__main__":
    sys.exit(main())
                    
