# Copyright 2021, Guillermo Adrian Molina.
# Copyright 2015 Cloudbase Solutions Srl
#
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

from oslo_config import cfg

from neutron_solaris.common.i18n import _

CONF = cfg.CONF


SOLARISVNIC_AGENT_GROUP_NAME = 'SOLARISVNIC'
DEFAULT_INTERFACE_MAPPINGS = []

SOLARISVNIC_AGENT_GROUP = cfg.OptGroup(
    SOLARISVNIC_AGENT_GROUP_NAME,
    title='Solaris Neutron Agent Options',
    help=('Configuration options for the neutron-solarisvnic-agent (L2 agent).')
)

SOLARISVNIC_AGENT_OPTS = [
    cfg.ListOpt('physical_interface_mappings',
                default=DEFAULT_INTERFACE_MAPPINGS,
                help=_("Comma-separated list of "
                       "<physical_network>:<physical_interface> tuples "
                       "mapping physical network names to the agent's "
                       "node-specific physical network interfaces to be used "
                       "for flat and VLAN networks. All physical networks "
                       "listed in network_vlan_ranges on the server should "
                       "have mappings to appropriate interfaces on each "
                       "agent.")),
]


ALL_OPTS = [
    (SOLARISVNIC_AGENT_GROUP, SOLARISVNIC_AGENT_OPTS)
]


def register_opts():
    for group, opts in ALL_OPTS:
        CONF.register_group(group)
        CONF.register_opts(opts, group=group)


def list_opts():
    return ALL_OPTS


register_opts()
