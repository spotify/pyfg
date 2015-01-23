First Steps
===========

Connecting to the device
------------------------

Let's start connecting to the vdom ``test_vdom`` for a particular device:

    >>> from pyFG import FortiOS
    >>> d = FortiOS('192.168.76.50', vdom='test_vdom')
    >>> d.open()

Loading configuration
---------------------

Now you can easily load a block of configuration and do some read operations:

    >>> d.load_configuration('router bgp')


We can verify easily that we got the configuration doing the following:

    >>> print d.running_config.to_text()
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
                edit 172.20.213.23
                  set remote-as 65555
                  set route-map-in "test4"
                next
                edit 2.2.2.2
                  set remote-as 123
                  set shutdown enable
                next
            end
            config redistribute rip
            end
            config redistribute6 ospf
            end
        end
    >>>

Or we can get the AS for each neighbor in a programmatic way:

    >>> for neigh, param in d.running_config['router bgp']['neighbor'].iterblocks():
    ...    print neigh, param.get_param('remote-as')
    ...
    172.20.213.23 65555
    2.2.2.2 123
    >>>

We can also iterate over all the parameters for a specific block. Let's get all the parameters for the neighbor 2.2.2.2:

    >>> for param, value in d.running_config['router bgp']['neighbor']['2.2.2.2'].iterparams():
    ...    print param, value
    ...
    remote-as 123
    shutdown enable

Adding a new sub block of configuration
---------------------------------------

Now, let's add a new bgp neighbor. First we have to create the configuration block and set the parameters:

    >>> from pyFG import FortiConfig
    >>> nn = FortiConfig(config_type='edit', name='3.3.3.3')
    >>> nn.set_param('remote-as', 12346)
    >>> nn.set_param('shutdown', 'enable')

Now we assign it to the candidate configuration and print it to see it looks like we want:

    >>> d.candidate_config['router bgp']['neighbor']['3.3.3.3'] = nn
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
                edit 172.20.213.23
                  set remote-as 65555
                  set route-map-in "test4"
                next
                edit 2.2.2.2
                  set remote-as 123
                  set shutdown enable
                next
                edit 3.3.3.3
                  set remote-as 12346
                  set shutdown enable
                next
            end
            config redistribute rip
            end
            config redistribute6 ospf
            end
        end
    >>>

Deleting a sub_block of configuration
-------------------------------------

Now, let's delete neighbor 2.2.2.2:

    >>> d.candidate_config['router bgp']['neighbor'].del_block('2.2.2.2')

Checking configuration changes
------------------------------

After all this changes let's see what has changed:

    >>> print d.compare_configuration()
    conf vdom
      edit test_vdom
        config router bgp
            config neighbor
                delete 2.2.2.2
                edit 3.3.3.3
                  set remote-as 12346
                  set shutdown enable
                next
            end
        end
    end
    >>>

As you can see, that method returns all the necessary commands to reach the candidate configuration from the running
configuration.

Setting a parameter
-------------------

Let's set a route-map outbound to neighbor 172.20.213.23:

    >>> d.candidate_config['router bgp']['neighbor']['172.20.213.23'].set_param('route-map-out', 'non-existant-routemap')

Committing changes
------------------

Now that we have done several changes let's commit the changes:

    >>> d.commit()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyFG/fortios.py", line 242, in commit
        self._commit(config_text, force)
      File "pyFG/fortios.py", line 297, in _commit
        raise exceptions.FailedCommit(wrong_commands)
    pyFG.exceptions.FailedCommit: [('-3', 'set route-map-out non-existant-routemap')]
    >>>

The route map we tried to assign does not exist so the commit failed returning a FailedCommit exception. By default,
if one single command fails during the commit operation the entire commit will be rolled back. At this point you have
three options:

 #. Create the route map
 #. Delete that parameter or assign an existing route-map
 #. Force the changes.

We are going to try forcing the changes:

    >>> d.commit(force=True)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyFG/fortios.py", line 242, in commit
        self._commit(config_text, force)
      File "pyFG/fortios.py", line 299, in _commit
        raise exceptions.ForcedCommit(wrong_commands)
    pyFG.exceptions.ForcedCommit: [('-3', 'set route-map-out non-existant-routemap')]
    >>> print d.compare_configuration()
    conf vdom
      edit test_vdom
        config router bgp
            config neighbor
                edit 172.20.213.23
                  set route-map-out non-existant-routemap
                next
            end
        end
    end
    >>>

We still got an exception although this time a different one; ForcedCommit. As you can see from the
compare_configuration method the rest of the changes went through.

Rolling back changes
--------------------

Now, let's assume we regret the changes we just did and we want to rollback:

    >>> d.rollback()
    >>> print d.running_config.to_text()
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
                edit 172.20.213.23
                  set remote-as 65555
                  set route-map-in "test4"
                next
                edit 2.2.2.2
                  set remote-as 123
                  set shutdown enable
                next
            end
            config redistribute rip
            end
            config redistribute6 ospf
            end
        end
    >>>

Voilà, we are back to our original configuration. BGP neighbor 3.3.3.3 is gone, 2.2.2.2 is back and that broken
parameter map is not in there anymore.

Closing the session
-------------------

Finally we close the ssh session:

    >>> d.close()