#!/usr/bin/env python

# Gets router bgp config from the device, then do some changes to the BGP parameters, deletes a neighbor,
# creates a new one, modifies another and computes the difference

from pyFG import FortiOS, FortiConfig
import sys

if __name__ == '__main__':
    hostname = sys.argv[1]

    d = FortiOS(hostname, vdom='vpn')
    d.open()
    d.load_config('router bgp')

    new_neigh = FortiConfig('10.6.6.8', 'edit')
    new_neigh.set_param('remote-as', '123')
    new_neigh.set_param('remotas', '123')
    d.candidate_config['router bgp']['neighbor'].set_block(new_neigh)
    d.candidate_config['router bgp']['neighbor']['10.6.6.6'].set_param('remote-as', '444')
    d.candidate_config['router bgp']['neighbor'].del_block('10.6.6.7')


    print "This is the diff of the configs:"
    for line in d.compare_config(text=True):
        print line

    print "This is how to reach the desired state:"
    config_changes = d.compare_config()
    print config_changes

    print "Result of applying the changes:"
    print d.commit(config_changes)

    d.close()
