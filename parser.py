import os
from os import walk
from os import system

# Atom format: (ddhhmmss, ip, port, protocol)

class parser:
	## Reads files in a directory, then deletes them. Also maintains a list of atoms
	# @param self
	# @param p file path
    def __init__(self, p):
        self.path = p
        self.atoms = []
	
	## Reads files in snort binary dump file format and deletes files when finished reading
    def read(self):
        
        info = os.walk(self.path)
        for root, dirs, files in info:
            for f in files:
                if f[0] == '.':
                    continue
                file_path = root + "/" + f
                os.system("sudo tcpdump -v -n -r " + file_path + " > asdf"+f[0:2])
                f2 = open("asdf"+f[0:2], "r")

                # Only want IP for now. Skip if not IP
                while True:
                    line1 = f2.readline()
                    words_line1 = line1.split()                    
                    while words_line1 and words_line1[1] != "IP":
                        line1 = f2.readline()
                        words_line1 = line1.split()
                    if not line1:
                        break
                    line2 = f2.readline()
                    words_line2 = line2.split()

                    if words_line1:
                        timestamp = words_line1[0].split(".",100)[0]
                    else:
                        timestamp = "---"
                    timestamp = timestamp.replace(":", "", 100)
                    if words_line1:
                        protocol = words_line1[13]
                    else:
                        protocol = "---"
                    source = words_line2[0]
                    destination = words_line2[2]
                    destination_words = destination.split(".")
                    formatted_destination = ""
                    for word in destination_words:
                        if word != destination_words[-1]:
                            formatted_destination = formatted_destination + word + "."
                    formatted_destination = formatted_destination.strip(".")
                    port = destination_words[-1]
                    self.atoms.append((timestamp, formatted_destination.strip(":"), port.strip(":"), protocol));

                
                # Add a delimiter for EOF not elegant but it should work
                self.atoms.append(("EOF","EOF","EOF","EOF"))
                f2.close()
                #os.system("sudo rm asdf")
                #os.system("sudo rm " + file_path)
	
	## Returns the first atoms from the list. If the list is empty, read files to add more back into the list
    def get_atom(self):
         
        if not self.atoms:
            self.read()

        if not self.atoms:
            return None
        else:
            return self.atoms.pop(0)
