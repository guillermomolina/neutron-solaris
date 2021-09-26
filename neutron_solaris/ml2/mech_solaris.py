# Copyright (c) 2016 IBM Corp.
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

from neutron_lib.api.definitions import portbindings
from neutron_lib import constants
from neutron_lib.plugins.ml2 import api
from oslo_log import log

from neutron.plugins.ml2.drivers import mech_agent
from neutron_solaris import constants as s_constants

LOG = log.getLogger(__name__)
FLAT_VLAN = 0

class SolarisMechanismDriver(mech_agent.SimpleAgentMechanismDriverBase):
    """Attach to networks using Solaris VNIC agent.

    The SolarisMechanismDriver integrates the ml2 plugin with the
    solaris VNIC agent. Port binding with this driver requires the
    solaris VNIC agent to be running on the port's host, and that agent
    to have connectivity to at least one segment of the port's
    network.
    """

    def __init__(self):
        super(SolarisMechanismDriver, self).__init__(
            s_constants.AGENT_TYPE_SOLARIS,
            s_constants.VIF_TYPE_SOLARIS,
            {portbindings.CAP_PORT_FILTER: False})
        LOG.debug('__init__ called')
       

    def get_allowed_network_types(self, agent):
        LOG.debug('get_allowed_network_types called')

        return [constants.TYPE_FLAT, constants.TYPE_VLAN]

    def get_mappings(self, agent):
        LOG.debug('get_mappings called')
        return agent['configurations'].get('interface_mappings', {})

    def check_vlan_transparency(self, context):
        LOG.debug('check_vlan_transparency called')
        """Solaris driver vlan transparency support."""
        return False

    def _get_vif_details(self, context, agent, segment):
        LOG.debug('_get_vif_details called')
        network_type = segment[api.NETWORK_TYPE]
        if network_type == constants.TYPE_FLAT:
            vlan_id = FLAT_VLAN
        elif network_type == constants.TYPE_VLAN:
            vlan_id = segment[api.SEGMENTATION_ID]
        else:
            LOG.error("Network type not supported %s", network_type)

        physical_network = segment[api.PHYSICAL_NETWORK]
        physical_interface = self.get_mappings(agent).get(physical_network)
        if not physical_network or not physical_interface:
            LOG.error("No interface mappings for physical network %s",
                      physical_network)
        
        vif_details = self.vif_details.copy()
        vif_details[portbindings.VIF_DETAILS_VLAN] = str(vlan_id)
        vif_details[portbindings.VIF_DETAILS_PHYSICAL_INTERFACE] = physical_interface
        LOG.debug("VIF details %s ", vif_details)
        return vif_details

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        LOG.debug('try_to_bind_segment_for_agent called')
        if self.check_segment_for_agent(segment, agent):
            vif_details = self._get_vif_details(context, agent, segment)
            LOG.debug("Solaris network vif_details added to context binding: %s",
                      vif_details)
            context.set_binding(segment[api.ID], self.vif_type, vif_details)
            return True
        return False


    def check_segment_for_agent(self, segment, agent=None):
        LOG.debug('check_segment_for_agent called')
        """Check if segment can be bound.

        :param segment: segment dictionary describing segment to bind
        :param agent: agents_db entry describing agent to bind or None
        :returns: True if segment can be bound for agent
        """
        network_type = segment[api.NETWORK_TYPE]
        if network_type in self.get_allowed_network_types(agent):
            if agent:
                mappings = self.get_mappings(agent)
                LOG.debug("Checking segment: %(segment)s "
                          "for mappings: %(mappings)s ",
                          {'segment': segment, 'mappings': mappings})
                return segment[api.PHYSICAL_NETWORK] in mappings
            return True
        return False

