# Copyright 2021, Guillermo Adrian Molina.
# Copyright 2013 Cloudbase Solutions SRL
# Copyright 2013 Pedro Navarro Perez
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
Unit tests for Oracle Solaris virtual switch neutron driver
"""

import sys
from unittest import mock


from neutron_solaris.agent import solaris_neutron_agent as \
    solaris_agent
from neutron_solaris.tests import base



class TestMain(base.BaseTestCase):

    @mock.patch.object(solaris_agent, 'SolarisNeutronAgent')
    @mock.patch.object(solaris_agent, 'common_config')
    @mock.patch.object(solaris_agent, 'neutron_config')
    def test_main(self, mock_config, mock_common_config, mock_solaris_agent):
        solaris_agent.main()

        mock_config.register_agent_state_opts_helper.assert_called_once_with(
            solaris_agent.CONF)
        mock_common_config.init.assert_called_once_with(sys.argv[1:])
        mock_config.setup_logging.assert_called_once_with()
        mock_solaris_agent.assert_called_once_with()
        mock_solaris_agent.return_value.daemon_loop.assert_called_once_with()
