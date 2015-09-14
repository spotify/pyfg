SSH Config
==========

You can now store some of the access details for your FortiGate appliacnes
inside the ~/.ssh/config of the user. Currently supported:

- Username
- Hostname
- Proxy Command
- IdentityFile

Example 1
---------

Simple "alias" whereas you would use the 'hostname' "fortigate" inside your
scripts instead of the IP address. Handy if you do not have a DNS server::

    Host fortigate
      Hostname 192.168.1.1
      User admin

Example 2
---------

A bit more complex for when you need go via a SSH proxy server to reach the 
appliance::

    Host fortigate
      Hostname 192.168.1.1
      User admin
      ProxyCommand ssh user@10.10.10.1 nc %h %p

