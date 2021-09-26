# Copyright 2015 Cloudbase Solutions SRL
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Unit tests for the Solaris Mechanism Driver.
"""

from unittest import mock

from neutron_solaris import constants
from neutron_solaris.ml2 import mech_solaris
from neutron_solaris.tests import base


class TestSolarisMechanismDriver(base.BaseTestCase):

    def setUp(self):
        super(TestSolarisMechanismDriver, self).setUp()
        self.mech_solaris = mech_solaris.SolarisMechanismDriver()

    def test_get_allowed_network_types(self):
        agent = {'configurations': {'tunnel_types': []}}
        actual_net_types = self.mech_solaris.get_allowed_network_types(agent)

        network_types = [constants.TYPE_LOCAL, constants.TYPE_FLAT,
                         constants.TYPE_VLAN, constants.TYPE_VXLAN]
        self.assertEqual(network_types, actual_net_types)

    def test_get_mappings(self):
        agent = {'configurations': {
            'interface_mappings': [mock.sentinel.mapping]}}
        mappings = self.mech_solaris.get_mappings(agent)
        self.assertEqual([mock.sentinel.mapping], mappings)

    def test_physnet_in_mappings(self):
        physnet = 'test_physnet'
        match_mapping = '.*'
        different_mapping = 'fake'

        pattern_matched = self.mech_solaris.physnet_in_mappings(
            physnet, [match_mapping])
        self.assertTrue(pattern_matched)

        pattern_matched = self.mech_solaris.physnet_in_mappings(
            physnet, [different_mapping])
        self.assertFalse(pattern_matched)

        pattern_matched = self.mech_solaris.physnet_in_mappings(
            physnet, [different_mapping, match_mapping])
        self.assertTrue(pattern_matched)
