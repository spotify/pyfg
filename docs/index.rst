.. pyFG documentation master file, created by
   sphinx-quickstart on Sun Oct 26 10:36:17 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyFG's documentation!
================================

This library does not pretend to hide or abstract FortiOS configuration. Its sole purpose is to give you a
a programmatic way to read it and modify it. To be able to use you will still need to understand how the CLI works.

There are two main libraries:

    * :class:`~pyFG.fortios.FortiOS` -- This is the main library you will use. It allows you to connect to a device, \
        read its configuration, it provides an interface to the running and the candidate config and provides diff and \
        commit operations amongst others.
    * :class:`~pyFG.forticonfig.FortiConfig` -- This library represents a block of configuration. You will usually \
        deal with this just to create new objects (like a new firewall policy) or just via the attribures \
        running_config and candidate_config in a :class:`~pyFG.fortiOS.FortiOS` object.


Tutorials
=========
.. toctree::
   :maxdepth: 2

   first_steps
   loading_config_from_file

Options
=======
.. toctree::
   :maxdepth: 2

   ssh_config.rst
   
Classes
=======

.. toctree::
   :maxdepth: 2

   fortios
   forticonfig
