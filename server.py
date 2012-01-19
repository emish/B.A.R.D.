import threading, socket, sys, re, httplib, os

#default server host and port number
host,port_num = "localhost", 9999

#two files: whitelist, blacklist
## shared whitelist, need lock
white_lock = threading.Lock()
## shared history, need lock
black_lock = threading.Lock()

whitelist = 'whitelist'
blacklist = 'blacklist'

class slave_thread(threading.Thread):
	
	## Initializes the thread class
	# @param conn Connection
	# @ param addr Address
    def __init__(self, conn,addr):
        threading.Thread.__init__(self)
        self.conn,self.addr = conn,addr
        self.name = "";

    ## Gets data from connection.
    # 1 = white, 2 = black
    def get_data(self):
        """server_thread.get_data() -> data 
        
        If the connection goes down, returns 0 length
        string. Otherwise, buffers the data and returns it as a
        string."""

        data = []
        while 1:
            d = self.conn.recv(1024)
            data.extend(d)
            if len(d)<1024: break
        return "".join(data)

    def add_blacklist(self, atom):
        black_lock.acquire()
        try:
            blacklist_f = open(blacklist, 'a')
            blacklist_f.write(atom)
            blacklist_f.close()
        except:
            print "Error. Invalid file location."
            black_lock.release()
            sys.exit()

        black_lock.release()

    def add_whitelist(self, atom):
        print "We are def in the mehtod now!"
        white_lock.acquire()
        try:
            print "mohohohohoho"
            whitelist_f = open(whitelist, 'a')
            whitelist_f.write(atom)
            whitelist_f.close()
            print "add_whitelist method"
        except:
            print "Error. Invalid file location."
            white_lock.release()
            sys.exit()

        white_lock.release()

	## The main thread loop. Receives message from the client, echoes them back and logs them in the history lists. Once a socket error or a 0 length string is received, the loop breaks, the socket is closed and the thread returns.
    def run(self):
        """run() -> None"""

        #helper to keep track of which mode you are in
        message = False
        
        while 1:
            try:

                #first get information from the socket
                data = self.get_data()

                #report it
                print "Got:",data

                #send it back
                if data == "1": #user has chosen to update whitelist
                    self.conn.send("whitelist")
                    atom = self.get_data()
                    print atom
                    self.add_whitelist(atom)
                    print "added to the whitelist"
                    self.conn.send("ok")
                elif data == "2": #user has chosen to update blacklist
                    self.conn.send("blacklist")
                    atom = self.get_data()
                    self.add_blacklist(atom)
                    self.conn.send("ok")
                elif data == "3": #send user whitelist
                    white_lock.acquire()
                    whitelist_f = open(whitelist, 'r')
                    strTosend = ""
                    for line in whitelist_f:
                        strTosend += line
                    self.conn.send(strTosend)
                    whitelist_f.close()
                    white_lock.release()
                elif data == "4": #send user blacklist
                    black_lock.acquire()
                    blacklist_f = open(blacklist, 'r')
                    strTosend = ""
                    for line in blacklist_f:
                        strTosend += line
                    self.conn.send(strTosend)
                    blacklist_f.close()
                    black_lock.release()
                elif data == "exit" or not data: #check 0 data here
                    break #break loop
                else:
                    self.conn.send("error")
                    break
            except (KeyboardInterrupt,EOFError):
                #capture Ctrl-C and Ctrl-D, exit smoothly
                break #we're out of here
            except socket.error,e:
                print >>sys.stderr, "Got a socket error in server thread:",str(e)
                break 
        self.conn.close() #close up, we're done
        print "Thread from,",self.addr,"is closing"

## Main method allows user to specify port number for server using -p flag
def main(argv):
    global port_num

    #allow user to specify port number for server
    if len(argv) == 2 and argv[0] == '-p':
        try:
            port_num = int(argv[1])
        except:
            print "Error. Invalid port number input."
            sys.exit()
    else:
        print "Invalid command line arguments."
        sys.exit()

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        sock.bind((host, port_num))
    except:
        print "Error. Cannot connect to port."
        sys.exit()

    sock.listen(5)
    print "Server Started on:", (host,port_num)

    #listen for a new client connections and spawn a thread to deal with it
    while 1: 
        try:
            conn,addr = sock.accept()
            print "New connection from:", addr
            th = slave_thread(conn,addr)
            th.start()
        except socket.error,e:
            print >>sys.stderr, "Got an error in accept:",str(e)
            break
        except KeyboardInterrupt:
            #Ctrl-C capture

            #no guarantee that this thread will recieve the signal,
            #but at some point, it should after multiple attempts
            print "Exiting ..."
            break
            
    sock.close() #close the server socket

if __name__ == "__main__":
    main(sys.argv[1:])
