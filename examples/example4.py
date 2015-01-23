#!/usr/bin/env python

# Gets router bgp config from the device, then do some changes to the BGP parameters, deletes a neighbor,
# creates a new one, modifies another and computes the difference

from pyFG import FortiOS, FortiConfig

if __name__ == '__main__':
    f = open('running.conf', 'r')
    running = f.read()
    f.close()

    d = FortiOS('')
    d.load_config(config_text=running)

    d.candidate_config['router bgp'].set_param('as', 123)
    d.candidate_config['router bgp']['neighbor']['10.240.4.3'].set_param('bfd', 'disable')
    d.candidate_config['router bgp']['neighbor'].del_block('10.240.4.24')

    new_neigh = FortiConfig('10.6.6.6', 'edit')
    new_neigh.set_param('as', '666')
    new_neigh.set_param('route-map-out', 'my_route_map')
    new_neigh.set_param('update-source', 'port6')
    new_neigh.set_param('bfd', 'enable')
    d.candidate_config['router bgp']['neighbor'].set_block(new_neigh)

    print "This is the diff of the conigs:"
    for line in d.compare_config(text=True):
        print line

    print "\n\n"
    print "This is how to reach the desired state:"
    print d.compare_config()