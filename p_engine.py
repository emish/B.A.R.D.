#!/usr/bin/python # p_engine.py
#import parser
import test_parser
## @class Pengine
#  @author The Bard Team
#  @version 1.1
class Pengine:

    window_size = 10000 #must be in ddhhmmss form

    ## A new Pengine object is initialized by the Bard
    #  module to track atoms and their persistence
    #  @param self
    #  @param frame_sizes tuple of frame sizes
    #  @param max_atoms the maximum number of atoms Pengine will track for persistence
    #  @param path The path where the Snort binary dumps can be found
    #  @param p_star The threshold ratio for significant atom persistence within a frame
    def __init__(self, frame_sizes, max_atoms, path, p_star):
        self.t_0 = 0
        self.t_1 = Pengine.window_size
        self.max_frame_size = max(frame_sizes)
        self.frame_sizes = frame_sizes
        self.atom_list = []
        self.persistent_list = []
        self.bitmaps = {}
        self.id_list = []
        self.max_ids = max_atoms
        #self.parser = parser.parser(path)
        self.parser = test_parser.test_parser(path)
        self.p_star = p_star

    ## @class Atom
    #  @author The Bard Team
    #  @version 1.1
    class Atom:
        ## Initialize a new atom object with defaul ID -1 that may or may not
        #  added to existing Bard data structures
        #  @param ip The destination ip
        #  @param port The destination port
        #  @param protocol The protocol of the packet
        #  @param timestamp When the packet was received
        def __init__(self, ip, port, protocol, timestamp):

            self.id = -1;
            self.dest_ip = ip
            self.dest_port = port
            self.protocol = protocol
            self.last_timestamp = timestamp
    
    ## The method called by the Bard module to process a file of Snort output into atom data
    #  @param self
    #  @returns List of persistent atoms found in this batch/file of Snort output
    def run(self):

        self.persistent_list = []

        a = self.getAtomObject()
        counter = 0
        while(a == None):
            a = self.getAtomObject()
        while(a.last_timestamp != "EOF"):
            while self.timeCheck(a) == 1:
                self.cleanBitmap()
            
            self.addAtom(a)
            #now the atom must exist
            self.updateBitmap(self.atomExists(a))
            
            a = self.getAtomObject()
            while(a == None):
               a = self.getAtomObject()
        return self.persistent_list

    ## Translates the atom tuple received from Parser.py into an Atom object
    #  @param self
    #  @returns The newly created Atom object
    def getAtomObject(self):
        temp = self.parser.get_atom()
        if temp:
            a = self.Atom(temp[1],temp[2],temp[3],temp[0])
            return a
        else:
            return None 

    ## Returns the smallest unused atom id or the id of the least recently seen atom which is now paged out of memory
    #  @param self
    #  @returns The id of the new Atom object in need of an ID
    def getID(self):
        id_list = self.id_list
        if len(id_list) < self.max_ids:
            id_list.insert(0, len(id_list))
            self.bitmaps[len(id_list) - 1] = [0] * self.max_frame_size
            return len(id_list) - 1
        else:
            old_id = id_list[-1]
            self.bitmaps[old_id] = [0] * self.max_frame_size
            id_list.pop()
            id_list.insert(0, old_id)
            return old_id
            
    ## Updates the atom's bitmap to reflect a sighting
    #  during the current window.
    #  @param atom The atom who's bitmap is to be updated.
    def updateBitmap(self, atom):

        self.bitmaps[atom.id][-1] = 1
        self.persistence(atom)

    ## Determines whether an atom is persistent based on its maximum ratio of windows seen
    #  to frame size compared to a predetermined threshold and, if so, adds the atom to the
    #  persistent_atom list
    #  @param self
    #  @param atom The atom being checked for persistence
    def persistence(self, atom):
        if not atom in self.persistent_list:
            temp = []
            for s in self.frame_sizes:
                temp.append(sum(self.bitmaps[atom.id][-s:self.max_frame_size])/s)
            if(max(temp) > self.p_star):
                self.persistent_list.append(atom)

    ## Removes all windows no longer in frame and adds new windows for latest part of frame.
    #  @param self
    def cleanBitmap(self):
        for k,v in self.bitmaps.iteritems():
            v.pop(0)
            v.append(0)
        
    ## Determines whether the current atom already exists in bard's data
    #  structures and if it does it updates its last_timestamps and returns it
    #  @param a The atom that is being checked
    #  @return existing The identical atom that already exists (if there is one)
    def atomExists(self,a):

        for b in self.atom_list:
            if compareAtoms(a,b):
                b.last_timestamp = a.last_timestamp
                #brings this atom to the front of the id_lists
                self.id_list.remove(b.id)
                self.id_list.insert(0, b.id)
                return b
        return None
        
    ## Adds a premade atom to the atom_list. If it already exists in the list, do nothing
    #  @param a The atom that is being added
    #  @return (1) if new atom and added, (0) if no action was taken        
    def addAtom(self,a):

        if self.atomExists(a) == None:
            self.atom_list.append(a)
            a.id = self.getID()
            return 1
        return 0

    ## Updates local time-keeping variables based on latest atom timestamp.
    #  @param a The atom to use
    #  @return Was the time updated?
    def timeCheck(self,a):

        t_0,t_1 = self.t_0,self.t_1
        a_time = int(a.last_timestamp)
        if t_0 > t_1: # Corner case when entire timestamp is to be reset
            t_0_tmp = timeIncrement(t_0)
            t_1_tmp = timeIncrement(t_1)
            a_time_tmp = timeIncrement(a_time)
            if a_time_tmp > t_1_tmp:
                self.t_0 = timeIncrement(t_0)
                self.t_1 = timeIncrement(t_1)
                return 1# + self.timeCheck(a)
        elif (a_time < t_1 and a_time < t_0) or a_time > t_1:
            self.t_0 = timeIncrement(t_0)
            self.t_1 = timeIncrement(t_1)
            return 1# + self.timeCheck(a)
        return 0

## Increments global time based on certain rules such as wrap around for days.
#  @param time The time to increment
#  @param amt By how much to increment. Default is 1hr= 00 01 0000
#  @return time The incremented time. 
def timeIncrement(time, amt=Pengine.window_size):

    mmss = time % 10000
    hh = time/10000 % 100
    hh += amt/10000 % 100
    if mmss == 0:
        hh = hh % 25
    else:
        hh = hh % 24
    time_u = hh*(10000) + mmss
    return time_u


## Compare two atoms objects to see if they identify the same actual
#  atom based on dest_ip, dest_port and protocol
#  @param a The first atom being compared
#  @param b The second atom being compared
#  @returns Boolean of whether the atoms are identical (1) or not (0)
def compareAtoms(a,b):
    if(a.dest_ip != b.dest_ip):
        return 0
    elif (a.dest_port != b.dest_port):
        return 0
    elif (a.protocol != b.protocol):
        return 0
    return 1
