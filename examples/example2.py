#!/usr/bin/env python
# Gets the router bgp config and prints it

from pyFG import FortiOS
import sys

if __name__ == '__main__':
    hostname = sys.argv[1]

    d = FortiOS(hostname, vdom='vpn')
    d.open()
    d.load_config('router bgp')
    d.close()

    for neighbor, config in d.running_config['router bgp']['neighbor'].iterblocks():
        print neighbor
        print "   AS: %s" % config.get_param('remote-as')
        print "   route-map-out: %s" % config.get_param('route-map-out')
        print "   route-map-in: %s" % config.get_param('route-map-in')

