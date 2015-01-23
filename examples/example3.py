#!/usr/bin/env python

#Gets router bgp config from the device, then loads a file with the new bgp config we want and we
#compute the difference

from pyFG import FortiOS
import sys

if __name__ == '__main__':
    f = open('candidate.conf', 'r')
    candidate = f.read()
    f.close()

    hostname = sys.argv[1]

    d = FortiOS(hostname, vdom='vpn')
    d.open()
    d.load_config('router bgp', empty_candidate=True)
    d.load_config(config_text=candidate, in_candidate=True)
    d.close()

    print "This is the diff of the conigs:"
    for line in d.compare_config(text=True):
        print line

    print "\n\n"
    print "This is how to reach the desired state:"
    print d.compare_config()