## Generates rules from atoms determined to be a bot
class rule_generator:
	## Makes sure p points to wherever the blacklist directory is located. SIDs for rules have to be unique, so must be sure to initate the generator with an acceptable starting rule number.
	# @param self
	# @param p path to blacklist
	# @param sid_start starting rule number
    def __init__(self, p, sid_start):
     
        self.path = p
        self.sid = sid_start
	## Takes an atom and writes a rule to block future instances
	# @param self
	# @ param _atom atom to be blocked
    def block(self, _atom):
        
        if not _atom:
            print "Empty atom"
            return None
        else:
            (timestamp, destination, port, protocol) = _atom
            rules_file = "blacklist"
            f = open(self.path + "/blacklist", "a")
            rule = "\nblock " + protocol + " $HOME_NET any <> " + destination + "." + port + " (sid:" + str(self.sid) + ")"
            f.write(rule)
            f.close()
            self.sid = self.sid + 1
            return rule
