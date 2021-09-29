# Copyright 2021, Guillermo Adrian Molina.
# Copyright 2014 OpenStack Foundation
# All Rights Reserved.
#
# Copyright (c) 2015, Oracle and/or its affiliates. All rights reserved.
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

import jinja2
import netaddr
from oslo_config import cfg
from oslo_log import log as logging
import six

from neutron.agent.linux import utils
from neutron.common import constants


LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt('ra_confs',
               default='$state_path/ra',
               help=_('Location to store IPv6 RA config files')),
]

cfg.CONF.register_opts(OPTS)

NDP_SMF_FMRI = 'svc:/network/routing/ndp:default'

# The configuration file for ndpd daemon expects all the 'key value' to be
# on the same line as that of the interface. For example:
#
# if net0  AdvSendAdvertisements on MinRtrAdvInterval 3 MaxRtrAdvInterval 10
# prefix 3234234 net0 AdvOnLinkFlag on AdvAutonomousFlag on
CONFIG_TEMPLATE = jinja2.Template(
    """if {{ interface_name }} """
    """ AdvSendAdvertisements on MinRtrAdvInterval 3 MaxRtrAdvInterval 10 """
    """ {% if ra_mode == constants.DHCPV6_STATELESS %} """
    """ AdvOtherConfigFlag on """
    """ {% endif %} """
    """ {% if ra_mode == constants.DHCPV6_STATEFUL %} """
    """ AdvManagedFlag on """
    """ {% endif %} """
    """ {% if ra_mode in (constants.IPV6_SLAAC, """
    """ constants.DHCPV6_STATELESS) %} """
    """\nprefix {{ prefix }} {{ interface_name }} """
    """ AdvOnLinkFlag on AdvAutonomousFlag on """
    """ {% endif %} """)


class NDPD(object):
    """Manage the data and state of Solaris in.ndpd daemon"""

    def __init__(self, router_id, dev_name_helper):
        self._router_id = router_id
        self._dev_name_helper = dev_name_helper

    def _generate_ndpd_conf(self, router_ports):
        ndpd_conf = utils.get_conf_file_name(cfg.CONF.ra_confs,
                                             self._router_id,
                                             'ndpd.conf', True)
        buf = six.StringIO()
        for p in router_ports:
            prefix = p['subnets'][0]['cidr']
            if netaddr.IPNetwork(prefix).version == 6:
                interface_name = self._dev_name_helper(p['id'])
                ra_mode = p['subnets'][0]['ipv6_ra_mode']
                buf.write('%s\n' % CONFIG_TEMPLATE.render(
                    ra_mode=ra_mode,
                    interface_name=interface_name,
                    prefix=prefix,
                    constants=constants))

        utils.replace_file(ndpd_conf, buf.getvalue())
        return ndpd_conf

    def _refresh_ndpd(self, ndpd_conf):
        cmd = ['/usr/sbin/svccfg', '-s', NDP_SMF_FMRI, 'setprop',
               'routing/config_file', '=', ndpd_conf]
        utils.execute(cmd)
        cmd = ['/usr/sbin/svccfg', '-s', NDP_SMF_FMRI, 'refresh']
        utils.execute(cmd)
        # ndpd SMF service doesn't support refresh method, so we
        # need to restart
        cmd = ['/usr/sbin/svcadm', 'restart', NDP_SMF_FMRI]
        utils.execute(cmd)
        LOG.debug(_("ndpd daemon has been refreshed to re-read the "
                    "configuration file"))

    def enable(self, router_ports):
        for p in router_ports:
            if netaddr.IPNetwork(p['subnets'][0]['cidr']).version == 6:
                break
        else:
            self.disable()
            return
        LOG.debug("enabling ndpd for router %s", self._router_id)
        ndpd_conf = self._generate_ndpd_conf(router_ports)
        self._refresh_ndpd(ndpd_conf)

    def disable(self):
        LOG.debug("disabling ndpd for router %s", self._router_id)
        utils.remove_conf_files(cfg.CONF.ra_confs, self._router_id)
        self._refresh_ndpd("")

    @property
    def enabled(self):
        cmd = ['/usr/bin/svcs', '-H', '-o', 'state', NDP_SMF_FMRI]
        stdout = utils.execute(cmd)
        return 'online' in stdout
