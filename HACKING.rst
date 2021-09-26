neutron-solaris Style Commandments
====================================

Read the OpenStack Style Commandments https://docs.openstack.org/hacking/latest/

Patches
-------


- nova_compute:

[gmolina@testp1-1:~]$ diff /home/gmolina/.virtualenvs/openstack/lib/python3.7/site-packages/oslo_messaging/_drivers/impl_rabbit.py /tmp/impl_rabbit.py 
961c961
<             if sys.platform != 'win32' and sys.platform != 'darwin' and sys.platform != 'sunos5':
---
>             if sys.platform != 'win32' and sys.platform != 'darwin':


(openstack) [gmolina@testp1-1:~]$ diff /home/gmolina/.virtualenvs/openstack/lib/python3.7/site-packages/nova/nova/virt/driver.py /tmp
1816c1816
<             compute_driver,
---
>             'nova.virt.%s' % compute_driver,


- neutron_server:

root@docker5:~# docker exec -it -u root neutron_server bash
(neutron-server)[root@docker5 /]# git clone https://github.com/guillermomolina/neutron-solaris.git
(neutron-server)[root@docker5 /]# cd neutron-solaris/
(neutron-server)[root@docker5 neutron-solaris]# pip install .


root@docker5:~# diff /etc/kolla/neutron-server/ml2_conf.ini /tmp/
4c4
< mechanism_drivers = linuxbridge,l2population,solaris
---
> mechanism_drivers = linuxbridge,l2population
docker restart neutron_server
