#!/usr/bin/env python
# Gets the entire config and prints it

from pyFG import FortiOS
import sys


if __name__ == '__main__':
    hostname = sys.argv[1]

    d = FortiOS(hostname, vdom='vpn')
    d.open()
    d.load_config('router bgp')
    d.close()
    print d.running_config.to_text()