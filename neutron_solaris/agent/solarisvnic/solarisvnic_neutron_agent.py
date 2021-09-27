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

import os
import sys

from neutron_lib.agent import topics
from neutron_lib.utils import helpers
from oslo_log import log as logging
import oslo_messaging
from oslo_service import service

from neutron.common import config as common_config
from neutron.conf.agent import common as neutron_config
from neutron.api.rpc.handlers import securitygroups_rpc as sg_rpc
from neutron.plugins.ml2.drivers.agent import _agent_manager_base as amb
from neutron.plugins.ml2.drivers.agent import _common_agent as ca

from neutron_solaris import config
from neutron_solaris import constants
from neutron_solaris.solaris import net_lib

CONF = config.CONF
LOG = logging.getLogger(__name__)

class SolarisVNICRPCCallBack(sg_rpc.SecurityGroupAgentRpcCallbackMixin,
                         amb.CommonAgentManagerRpcCallBackBase):
    # Set RPC API version to 1.0 by default.
    # history
    #   1.1 Support Security Group RPC
    #   1.3 Added param devices_to_update to security_groups_provider_updated
    #   1.4 Added support for network_update
    #   1.5 Added support for binding_activate and binding_deactivate
    target = oslo_messaging.Target(version='1.5')

    def network_delete(self, context, **kwargs):
        LOG.debug("network_delete received")
        network_id = kwargs.get('network_id')

        if network_id not in self.network_map:
            LOG.error("Network %s is not available.", network_id)
            return

    def port_update(self, context, **kwargs):
        port = kwargs['port']
        LOG.debug("port_update received %s ", kwargs)
        LOG.debug("port_update received for port %s ", port)
        mac = port['mac_address']
        # Put the device name in the updated_devices set.
        # Do not store port details, as if they're used for processing
        # notifications there is no guarantee the notifications are
        # processed in the same order as the relevant API requests.
        self.updated_devices.add(mac)

    def network_update(self, context, **kwargs):
        network_id = kwargs['network']['id']
        LOG.debug("network_update message received for network "
                  "%(network_id)s",
                  {'network_id': network_id})

    def binding_activate(self, context, **kwargs):
        if kwargs.get('host') != self.agent.conf.host:
            return
        LOG.debug("binding_activate received for port %s ", port)
        mac = port['mac_address']
        # Put the device name in the updated_devices set.
        # Do not store port details, as if they're used for processing
        # notifications there is no guarantee the notifications are
        # processed in the same order as the relevant API requests.
        self.updated_devices.add(mac)

    def binding_deactivate(self, context, **kwargs):
        if kwargs.get('host') != self.agent.conf.host:
            return
        LOG.debug("binding_deactivate received for port %s ", port)
        mac = port['mac_address']
        # Put the device name in the updated_devices set.
        # Do not store port details, as if they're used for processing
        # notifications there is no guarantee the notifications are
        # processed in the same order as the relevant API requests.
        self.updated_devices.add(mac)


class SolarisVNICNetworkManager(amb.CommonAgentManagerBase):
    def __init__(self, interface_mappings):
        self.interface_mappings = interface_mappings
        self.validate_interface_mappings()
        self.mac_device_name_mappings = dict()

    def validate_interface_mappings(self):
        LOG.debug("validate_interface_mappings")
        for physnet, interface in self.interface_mappings.items():
            if not net_lib.Datalink.datalink_exists(interface):
                LOG.error("Interface %(intf)s for physical network "
                          "%(net)s does not exist. Agent terminated!",
                          {'intf': interface, 'net': physnet})
                sys.exit(1)

    def ensure_port_admin_state(self, device, admin_state_up):
        LOG.debug("Setting admin_state_up to %s for device %s",
                  admin_state_up, device)

    def get_agent_configurations(self):
        configuration = {'interface_mappings': self.interface_mappings}
        LOG.debug('Agent configuration called %s', str(configuration) )
        return configuration

    def get_agent_id(self):
        if self.interface_mappings:
            mac = net_lib.Datalink.get_mac(
                list(self.interface_mappings.values())[0])
        else:
            devices = self.ip.get_devices(True)
            for device in devices:
                mac = net_lib.Datalink.get_mac(device.name)
                if mac:
                    break
            else:
                LOG.error("Unable to obtain MAC address for unique ID. "
                          "Agent terminated!")
                sys.exit(1)
        agent_id = 'solaris%s' % mac.replace(":", "")
        LOG.debug("get_agent_id() = %s", str(agent_id))
        return agent_id

    def get_devices_modified_timestamps(self, devices):
        # TODO(kevinbenton): this should be implemented to detect
        # rapid Nova instance rebuilds.
        return {}

    def get_all_devices(self):
        devices = set()
        for device in net_lib.Datalink.get_vnic_names():
            mac = net_lib.Datalink.get_mac(device)
            self.mac_device_name_mappings[mac] = device
            devices.add(mac)
        LOG.debug("get_all_devices %s ",devices)
        return devices

    def get_extension_driver_type(self):
        LOG.debug("get_extension_driver_type %s ", constants.EXTENSION_DRIVER_TYPE)
        return constants.EXTENSION_DRIVER_TYPE

    def get_rpc_callbacks(self, context, agent, sg_agent):
        return SolarisVNICRPCCallBack(context, agent, sg_agent)

    def get_agent_api(self, **kwargs):
        pass

    def get_rpc_consumers(self):
        consumers = [[topics.PORT, topics.UPDATE],
                     [topics.NETWORK, topics.UPDATE],
                     [topics.SECURITY_GROUP, topics.UPDATE],
                     [topics.PORT_BINDING, topics.DEACTIVATE],
                     [topics.PORT_BINDING, topics.ACTIVATE]]
        return consumers

    def plug_interface(self, network_id, network_segment, mac,
                       device_owner):
        LOG.debug("Network segment: %s, MAC: %s, owner: %s", network_segment,
                  mac, device_owner)
        vnic_name = self.mac_device_name_mappings[mac]
        if not net_lib.Datalink.datalink_exists(vnic_name):
            LOG.error("VNIC %(intf)s does not exist!",
                      {'intf': vnic_name})
            return
        state = net_lib.Datalink.get_prop(vnic_name, 'state')
        LOG.debug("VNIC %s state is %s", vnic_name, state)
        return True
        

    def setup_arp_spoofing_protection(self, device, device_details):
        pass

    def delete_arp_spoofing_protection(self, devices):
        pass

    def delete_unreferenced_arp_protection(self, current_devices):
        pass


def parse_interface_mappings():
    if not CONF.SOLARIS.physical_interface_mappings:
        LOG.error("No physical_interface_mappings provided, but at least "
                  "one mapping is required. Agent terminated!")
        sys.exit(1)

    try:
        interface_mappings = helpers.parse_mappings(
            CONF.SOLARIS.physical_interface_mappings)
        LOG.info("Interface mappings: %s", interface_mappings)
        return interface_mappings
    except ValueError as e:
        LOG.error("Parsing physical_interface_mappings failed: %s. "
                  "Agent terminated!", e)
        sys.exit(1)


def validate_firewall_driver():
    fw_driver = CONF.SECURITYGROUP.firewall_driver
    supported_fw_drivers = ['neutron.agent.firewall.NoopFirewallDriver',
                            'noop']
    if fw_driver not in supported_fw_drivers:
        LOG.error('Unsupported configuration option for "SECURITYGROUP.'
                  'firewall_driver"! Only the NoopFirewallDriver is '
                  'supported by solaris agent, but "%s" is configured. '
                  'Set the firewall_driver to "noop" and start the '
                  'agent again. Agent terminated!',
                  fw_driver)
        sys.exit(1)

def main():
    neutron_config.register_agent_state_opts_helper(CONF)
    common_config.init(sys.argv[1:])
    neutron_config.setup_logging()

    validate_firewall_driver()
    interface_mappings = parse_interface_mappings()

    manager = SolarisVNICNetworkManager(interface_mappings)

    polling_interval = CONF.AGENT.polling_interval
    quitting_rpc_timeout = CONF.AGENT.quitting_rpc_timeout
    agent = ca.CommonAgentLoop(manager, polling_interval,
                               quitting_rpc_timeout,
                               constants.AGENT_TYPE_SOLARIS,
                               constants.AGENT_PROCESS_SOLARIS)
    LOG.info("Agent initialized successfully, now running... ")
    launcher = service.launch(CONF, agent, restart_method='mutate')
    launcher.wait()
