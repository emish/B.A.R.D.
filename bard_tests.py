## Unit tests for bard.py
#@file bard_tests.py
#@author The Bard Team
#@version 1.1
#@date 3 December 2010

import unittest
import bard

## This unit testing class is built around the "unittest" module.
## Running this file will automatically run each test_* method as a unit test.
#@class p_engine_tester
class bard_tester(unittest.TestCase):
    ## Instantiates variables needed for testing
    # @param self
    def setUp(self):
        bardy = bard.Bard()
        self.white_file = file("../test_data/test_whitelist", 'w')
        self.black_rules = file("../test_data/test_blackrules", 'w')
        self.fup = bard.FileUpdateThread()
             #remove this line and add any instantiations that are
             #more conveniently place here than repeatedly in methods
    
    ## Cleans up after testing is complete
    # @param self
    def tearDown(self):
        self.white_file.close()
        self.black_rules.close()
        pass #remove this line and add any cleanup


    #Unit tests for bard.py

    ## Test file updates
    def test_update_files(self):
        w_test = "a line of whitelist\n"
        b_test = "a line of black rules\n"
        self.fup.update_files(w_test, b_test)
        w_fp = file(bard.white_file, 'r')
        b_fp = file(bard.black_file, 'r')
        #print w_fp.readline()
        #print b_fp.readline()
        assert w_fp.readline() == w_test, "White file not equal"
        assert b_fp.readline() == b_test, "Black file not equal"

    def test_updateServer(self):
        pass

    ## Sample Test
    # List of test cases (if you want):
    # 1 . . .
    # 2 . . .
    # @param self
    def test_SampleTest(self):
        x = 1
        y = 2
        assert x + y == 3, '1 + 2 failed'
        y = self.helper_method(x, 6)
        assert x + y == 7, '6 + 1 failed'
        
    ## Helper method (Not used as a unit test since it does not begin
    ## with 'test_'
    # Returns first parameter * second parameter
    # @param self
	# @param param	First number
	# @param param2 Second number
    # @returns param * param2
    def helper_method(self, param, param2):
        return param * param2

if __name__ == "__main__":
        unittest.main()
