Loading configuration from a file
=================================

The following example is very interesting if you plan to manage your devices using a configuration management system
based in templates like ansible. Let's assume we have a configuration file that we have generated somehow with the
following content::

    config router bgp
            config neighbor
                edit "172.20.213.32"
                    set remote-as 333
                    set route-map-out "test4"
                next
            end
            config redistribute "connected"
            end
            config redistribute "rip"
            end
            config redistribute "ospf"
            end
            config redistribute "static"
            end
            config redistribute "isis"
            end
            config redistribute6 "connected"
            end
            config redistribute6 "rip"
            end
            config redistribute6 "ospf"
            end
            config redistribute6 "static"
            end
            config redistribute6 "isis"
            end
    end

We want to load that configuration into a device, replacing its current configuration. First we have to connect to the
device and load the running configuration we want to replace:

    >>> from pyFG import FortiOS
    >>> d = FortiOS('192.168.76.50', vdom='test_vdom')
    >>> d.open()
    >>> d.load_configuration('router bgp', empty_candidate=True)

The parameter ``empty_candidate`` will load only the running config. Now, we load the configuration file into the
candidate config:

    >>> with open ("bgp_config.txt", "r") as my_file:
    ...     data=my_file.read()
    ...
    >>> d.load_configuration(config_text=data, in_candidate=True)
    >>> print d.candidate_config.to_text()
    config router bgp
        config redistribute isis
        end
        config redistribute6 connected
        end
        config redistribute6 isis
        end
        config redistribute static
        end
        config redistribute6 rip
        end
        config redistribute connected
        end
        config redistribute ospf
        end
        config redistribute6 static
        end
        config neighbor
            edit 172.20.213.32
              set remote-as 333
              set route-map-out "test4"
            next
        end
        config redistribute rip
        end
        config redistribute6 ospf
        end
    end

Now you can check the differences like this:

    >>> print d.compare_configuration()
    conf vdom
      edit test_vdom
        config router bgp
            config neighbor
                delete 172.20.213.23
                delete 2.2.2.2
                edit 172.20.213.32
                  set remote-as 333
                  set route-map-out "test4"
                next
            end
        end
    end

And commit the changes:

    >>> d.commit()
    >>> print d.compare_configuration()
    >>>
    >>> d.close()

A final compare_configuration returning an empty string will prove us that our changes were applied correctly.