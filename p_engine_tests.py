## Unit tests for p_engine.py
#@file p_engine_test.py
#@author The Bard Team
#@version 1.1
#@date 17 November 2010

import unittest
import p_engine

## This unit testing class is built around the "unittest" module.
#@class p_engine_tester
class p_engine_tester(unittest.TestCase):
    ## Instantiates variables needed for testing
    # @param self
    def setUp(self):
        self.pengine = p_engine.Pengine([3],3,".",.5)
        self.atom = self.pengine.Atom('111.111.111.111',80,'tcp',0)
    ## Cleans up after testing is complete
    # @param self
    def tearDown(self):
        self.atom = None
        self.pengine = None
        
    #One test per method in p_engine.py
    
    ## Tests the Pengine __init__ method.
    # Does not test valididty of parser object
    # Test cases (frame_sizes, max_atoms, path): \n
    # Case 1: [1], 1, "" \n
    # Case 2: [9,1,4,7], 1, "" \n
    # Case 3: [8,5,3,10], 5, "" \n
    # Case 4: [1,4,3], 4, "./test_data"
    # @param self
    def test_Pengine(self):
        self.Pengine_helper([1], 1, "")
        self.Pengine_helper([9,1,4,7], 1, "")
        self.Pengine_helper([8,5,3,10], 5, "")
        self.Pengine_helper([1,4,3], 4, "./test_data")
        
    ## Helper method for test_Pengine.
    # Checks whether Pengine initial values have been set properly.
    # @param self, frame_sizes, max_atoms, path
    # @returns true or false, signifying validity of created Pengine
    def Pengine_helper(self, f, m, p):
        pengine = self.pengine
        pengine = p_engine.Pengine(f, m, p,.5)
        assert pengine.t_0 == 0, 't_0'
        assert pengine.t_1 == 10000, 't_1'
        assert pengine.max_frame_size == max(f), 'max_frame_size'
        assert pengine.frame_sizes == f, 'frame_sizes'
        assert pengine.atom_list == [], 'atom_list'
        assert pengine.bitmaps == {}, 'bitmaps'
        assert pengine.id_list == [], 'id_list'
        assert pengine.max_ids == m, 'max_ids'
        
    ## Tests the Atom __init__ method.
    # Test cases (ip, port, protocol, timestamp):
    # Case 1: '111.111.111.111',80,'tcp',0
    # Case 2: '11.31.121.34',80,'tcp',-1
    # Case 3: 
    # Case 4: 
    # @param self
    def test_Atom(self):
        self.Atom_helper('111.111.111.111',80,'tcp',0)
        self.Atom_helper('11.31.121.34',80,'tcp',1)
        
    ## Helper method for test_Atom.
    # Checks whether Atom initial values have been set properly.
    # @param self, ip, port, protocol, timestamp
    # @returns true or false, signifying validity of created atom
    def Atom_helper(self, ip, prt, ptcl, ts):
        atom = self.atom
        self.pengine = p_engine.Pengine([1],10,"",.5)
        atom = self.pengine.Atom(ip,prt,ptcl,ts)
        assert atom.id == -1, 'id'
        assert atom.dest_ip == ip, 'dest_ip'
        assert atom.dest_port == prt, 'dest_port'
        assert atom.protocol == ptcl, 'protocol'
        assert atom.last_timestamp == ts, 'last_timestamp'

    ## Tests the getID method of Pengine.
    # Test cases:
    # Case 1: check empty list
    # Case 2: getting first ID
    # Case 3: getting second ID
    # Case 4: getting third ID
    # Case 5: getting ID > maxIDs
    # Case 5: getting ID > maxIDs + 1
    # @param self
    def test_getID(self):
        pengine = self.pengine
        assert pengine.id_list == [], 'check empty list'
        assert pengine.getID() == 0, 'first ID == 0'
        assert pengine.id_list == [0], 'list now == [0]'
        assert pengine.bitmaps == {0:[0,0,0]}, 'bitmap now == {0:[0,0,0]}'
        assert pengine.getID() == 1, 'second ID == 1'
        assert pengine.id_list == [1,0], 'list now == [1,0]'
        assert pengine.bitmaps == {0:[0,0,0], 1:[0,0,0]}, 'bitmap now == {0:[0,0,0], 1:[0,0,0]}'
        assert pengine.getID() == 2, 'third ID == 2'
        assert pengine.id_list == [2,1,0], 'list now == [2,1,0]'
        assert pengine.bitmaps == {0:[0,0,0], 1:[0,0,0], 2:[0,0,0]}, 'bitmap now == {0:[0,0,0], 1:[0,0,0], 2:[0,0,0]}'
        assert pengine.getID() == 0, 'third ID == 0'
        assert pengine.id_list == [0,2,1], 'list now == [0,2,1]'
        assert pengine.bitmaps == {0:[0,0,0], 1:[0,0,0], 2:[0,0,0]}, 'bitmap now == {0:[0,0,0], 1:[0,0,0], 2:[0,0,0]}'
        assert pengine.getID() == 1, 'fourth ID == 1'
        assert pengine.id_list == [1,0,2], 'list now == [1,0,2]'    
        assert pengine.bitmaps == {0:[0,0,0], 1:[0,0,0], 2:[0,0,0]}, 'bitmap now == {0:[0,0,0], 1:[0,0,0], 2:[0,0,0]}'

    ## Tests the updateBitmap method of Pengine.
    # Test cases:
    # Case 1: check empty bitmap
    # Case 2: add one atom and check updated bitmap
    # Case 3: add second atom and check updated bitmap
    # @param self
    def test_updateBitmap(self):
        pengine = self.pengine;
        atom = self.atom
        assert pengine.bitmaps == {}, 'check empty bitmap'
        atom.id = pengine.getID()
        pengine.atom_list.append(atom)
        pengine.updateBitmap(atom)
        assert pengine.bitmaps == {0:[0,0,1]}
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port,\
                                 atom.protocol,atom.last_timestamp)
        atom_two.id = pengine.getID()
        pengine.atom_list.append(atom_two)
        assert pengine.bitmaps == {0:[0,0,1], 1:[0,0,0]}
        pengine.updateBitmap(atom_two)
        assert pengine.bitmaps == {0:[0,0,1], 1:[0,0,1]}
        pengine.cleanBitmap()
        assert pengine.bitmaps == {0:[0,1,0], 1:[0,1,0]}
        pengine.updateBitmap(atom)
        assert pengine.bitmaps == {0:[0,1,1], 1:[0,1,0]}
        pengine.updateBitmap(atom_two)
        assert pengine.bitmaps == {0:[0,1,1], 1:[0,1,1]}
        pengine.cleanBitmap()
        assert pengine.bitmaps == {0:[1,1,0], 1:[1,1,0]}

    ## Tests the timeIncrement method of Pengine.
    # Test cases (timestamps):
    # Case 1: 10000 (hours place . . .)
    # Case 2: 10412 (. . . with mmss nonzero)
    # Case 3: 230412 (hour to day conversion . . .)
    # Case 4: 6230412 (. . . with days nonzero)
    # Case 5: 99230000 (wrap around . . .)
    # Case 6: 99230576 (. . . with mmss nonzero)
    # @param self
    def test_timeIncrement(self):
        for h in range(0,230000,10000):
            for m in range(0,5900,100):
                for s in range(0,59):
                    if h == 230000 and mmss == 0:
                        assert p_engine.timeIncrement(h+m+s) == 240000, "230000 bumped"
                    elif h == 240000 and mmss == 0:
                        assert p_engine.timeIncrement(h+m+s) == 0, "day bumped"
                    elif h == 230000:
                        assert p_engine.timeIncrement(h+m+s) == m+s, "day bumped"
                    else:
                        assert p_engine.timeIncrement(h+m+s) == h+10000+m+s, "hour bumped"
        assert p_engine.timeIncrement(10000) == 20000, 'hours place'
        assert p_engine.timeIncrement(10412) == 20412, 'with mmss != 0'
        assert p_engine.timeIncrement(230000) == 240000, 'wrap around'
        assert p_engine.timeIncrement(230576) == 576, 'wrap around w/ mmss'

    ## Tests the timeCheck method of Pengine.
    # Test cases:
    # Case Set A: t0 < t1
    # Case 1: a_time = t0
    # Case 2: t0 < a_time < t1
    # Case 3: a_time = t1
    # Case 4: a_time > t1
    # Case Set B: t1 < t0 (wrap around)
    # Case 1: a_time = t0
    # Case 2: a_time < t0 < t1
    # Case 3: a_time = t1
    # Case 4: t1 < a_time < t0
    # @param self
    def test_timeCheck(self):
        #self.resetEngine()
        pengine = self.pengine
        atom = self.atom
        pengine.window_size = 10000

        # case 1: t0 < t1
        pengine.t_0 = 0
        pengine.t_1 = 10000
        assert pengine.timeCheck(atom) == 0, 'a_time = t0'
        atom.last_timestamp = int((pengine.t_0 + pengine.t_1) / 2)
        assert pengine.timeCheck(atom) == 0, 't0 < a_time < t1'
        atom.last_timestamp = int(pengine.t_1)
        assert pengine.timeCheck(atom) == 0, 'a_time = t1'
        atom.last_timestamp = int(pengine.t_1 + 10)
        assert pengine.timeCheck(atom) == 1, 'a_time > t1'
        
        # case 2: t1 < t0 (wrap around)
        pengine.t_0 = 99235959
        pengine.t_1 = p_engine.timeIncrement(pengine.t_0)
        atom.last_timestamp =  int(pengine.t_0)
        assert pengine.timeCheck(atom) == 0, 'a_time = t0'
        atom.last_timestamp = int(pengine.t_1 - 10)
        assert pengine.timeCheck(atom) == 0, 'a_time < t0 < t1'
        atom.last_timestamp = int(pengine.t_1)
        assert pengine.timeCheck(atom) == 0, 'a_time = t1'
        atom.last_timestamp = int(pengine.t_1 + 10)
        assert pengine.timeCheck(atom) == 1, 't1 < a_time < t0'

    ## Tests the compareAtoms method of Pengine.
    # Test cases:
    # Case 1: compare to self
    # Case 2: compare to equivalent atom
    # Case 3: compare to non-equivalent atom
    # Case 4: compare to self (using a different atom)
    # @param self
    def test_compareAtoms(self):
        #self.resetEngine()
        pengine = self.pengine
        atom = self.atom
        assert p_engine.compareAtoms(atom,atom) == 1, 'compare to self'
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port,\
                                 atom.protocol,atom.last_timestamp)
        assert p_engine.compareAtoms(atom,atom_two) == 1, 'compare to equivalent'
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port-1,\
                                 atom.protocol,atom.last_timestamp)
        assert p_engine.compareAtoms(atom,atom_two) == 0, 'compare to different'
        assert p_engine.compareAtoms(atom_two,atom_two) == 1, 'compare to self'
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port,\
                                 atom.protocol,atom.last_timestamp+1)
        assert p_engine.compareAtoms(atom_two,atom) == 1, 'different timestamp'

    ## Tests the atomExists method of Pengine.
    # Test cases:
    # Case 1: empty atom list
    # Case 2: one atom exists
    # Case 3: second atom that has not been added
    # Case 4: second atom exists
    # @param self
    def test_atomExists(self):
        #self.resetEngine()
        pengine = self.pengine
        atom = self.atom
        assert pengine.atomExists(atom) == None, 'empty atom list'
        pengine.atom_list.append(atom)
        atom.id = pengine.getID()
        assert pengine.atomExists(atom) == atom, 'one atom exists'
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port-1,\
                                 atom.protocol,atom.last_timestamp)
        assert pengine.atomExists(atom_two) == None, 'unadded atom dne'
        pengine.atom_list.append(atom_two)
        atom_two.id = pengine.getID()
        assert pengine.atomExists(atom_two) == atom_two, 'second atom exists'
 
    ## Tests the addAtom method of Pengine.
    # Test cases:
    # Case 1: add first atom
    # Case 2: add same atom
    # Case 3: add equivalent atom (should not be added)
    # Case 4: add second unique atom
    # Case 5: add same atom
    # Case 6: add equivalent atom
    # @param self
    def test_addAtom(self):
        #self.resetEngine()
        pengine = self.pengine
        atom = self.atom
        assert pengine.addAtom(atom) == 1, 'add first atom'
        assert pengine.addAtom(atom) == 0, 'add same atom 1'
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port,\
                                 atom.protocol,atom.last_timestamp)
        assert pengine.addAtom(atom_two) == 0, 'add equivalent atom'
        atom_two = pengine.Atom(atom.dest_ip,atom.dest_port-1,\
                                 atom.protocol,atom.last_timestamp)
        assert pengine.addAtom(atom_two) == 1, 'add second unique atom'
        assert pengine.addAtom(atom_two) == 0, 'add same atom 2'
        atom = pengine.Atom(atom_two.dest_ip,atom_two.dest_port,\
                                 atom_two.protocol,atom_two.last_timestamp)
        assert pengine.addAtom(atom) == 0, 'add equivalent atom'
 
    ## End to end test of Pengine
    # @param self
    def test_end_to_end(self):
        self.pengine = p_engine.Pengine([5,10,24],10000,".",.5)
        persistent_list = self.pengine.run()
        print "persistent atom count: ",
        print len(persistent_list)
        for a in persistent_list:
            print a.dest_ip
        

if __name__ == "__main__":
        unittest.main()
