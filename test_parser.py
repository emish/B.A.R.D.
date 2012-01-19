#import os
#from os import walk
#from os import system

# Atom format: (ddhhmmss, ip, port, protocol)

class test_parser:
    def __init__(self, p):
        """ Reads files in a directory, then deletes them."""
        """ Also maintains a list of atoms """
        self.path = p
        self.atoms = [];

    def read(self):
        """ Reads files (snort binary dumps). Delete files when finished reading"""
        
        #info = os.walk(self.path)
        #for root, dirs, files in info:
            #for f in files:
                #file_path = root + "/" + f
                #os.system("sudo tcpdump -v -n -r " + file_path + " > asdf")
        f2 = open("test.txt", "r")

        # Only want IP for now. Skip if not IP
        while True:
            line = f2.readline()
            words = line.split(",")
            if not line:
                break

            timestamp = words[0]
            destination = words[1]
            port = words[2]
            protocol = words[3]
            self.atoms.append((timestamp, destination, port, protocol));

        
        # Add a delimiter for EOF not elegant but it should work
        self.atoms.append(("EOF","EOF","EOF","EOF"))
        f2.close()
        #os.system("sudo rm asdf")
        #os.system("sudo rm " + file_path)

    def get_atom(self):
        """ Returns the first atom from the list. If the list is empty, read files to add more back into the list """
        
        if not self.atoms:
            self.read()

        if not self.atoms:
            return None
        else:
            return self.atoms.pop(0)

    def block(self, _atom):
        """ Takes an atom and writes a rule to block future instances """
        
        if not _atom:
            print "Empty atom"
            return -1
        else:
            (timestamp, destination, port, protocol) = _atom
            rules_file = "blacklist"
            f = open(rules_file, "a")
            f.write("\ndrop " + protocol + " $HOME_NET any <> " + destination + "." + port)
            f.close()
            return 1
