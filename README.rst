=================
neutron-solaris
=================

This project tracks the work to integrate the Solaris networking with Neutron.
This project contains the Solaris Neutron Agent, Security Groups Driver, and
ML2 Mechanism Driver, which are used to properly bind neutron ports on a
Solaris host.

This project resulted from the neutron core vendor decomposition.

Supports Python 2.7, Python 3.3, Python 3.4, and Python 3.5.

* Free software: Apache license
* Documentation: https://github.com/guillermomolina/neutron-solaris/wiki
* Source: https://github.com/guillermomolina/neutron-solaris
* Bugs: https://github.com/guillermomolina/neutron-solaris/issues
* Release notes: 

How to Install
--------------

Run the following command to install the agent on the system:

::

    [neutron-solaris]$  python setup.py install

To use the ``neutron-solaris-agent``, the Neutron Controller will have to be
properly configured. For this, the config option ``core_plugin`` in the
``/etc/neutron/neutron.conf`` file must be set as follows:

::

    core_plugin = neutron.plugins.ml2.plugin.Ml2Plugin

Additionally, ``solaris`` will have to be added as a mechanism driver in the
``/etc/neutron/plugins/ml2/ml2_conf.ini`` configuration file:

::

    mechanism_drivers = openvswitch,solaris

In order for these changes to take effect, the ``neutron-server`` service will
have to be restarted.

Finally, make sure the ``tenant_network_types`` field contains network types
supported by Solaris: local, flat, vlan, vxlan.


Tests
-----

You will have to install the test dependencies first to be able to run the
tests.

::

    [neutron-solaris]$  pip install -r requirements.txt
    [neutron-solaris]$  pip install -r test-requirements.txt

You can run the unit tests with the following command.

::

    [neutron-solaris]$  nosetests neutron_solaris\tests


How to contribute
-----------------

To contribute to this project, please go through the following steps.

1. Clone the project and keep your working tree updated.
2. Make modifications on your working tree.
3. Run unit tests.
4. If the tests pass, commit your code.
5. Submit your code via ``git review -v``.
6. Check that Jenkins and the Microsoft Solaris CI pass on your patch.
7. If there are issues with your commit, amend, and submit it again via
   ``git review -v``.
8. Wait for the patch to be reviewed.


Features
--------

* Supports Flat, VLAN, VxLAN network types.
* Supports Neutron Security Groups.
* Contains ML2 Mechanism Driver.
* Parallel port processing.

Run
---

::

    neutron-solaris-agent --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/solaris_agent.ini