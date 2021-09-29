# Copyright 2021, Guillermo Adrian Molina.
# Copyright 2013 Cloudbase Solutions SRL
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


AGENT_TOPIC = 'q-agent-notifier'
AGENT_TYPE_SOLARISVNIC = 'Solaris agent'
AGENT_PROCESS_SOLARISVNIC = 'neutron-solarisvnic-agent'
VIF_TYPE_SOLARISVNIC = 'solaris'
EXTENSION_DRIVER_TYPE = 'solaris'


# Special vlan_id value in ovs_vlan_allocations table indicating flat network
FLAT_VLAN_ID = -1

TYPE_FLAT = 'flat'
TYPE_LOCAL = 'local'
TYPE_VLAN = 'vlan'
TYPE_VXLAN = 'vxlan'
