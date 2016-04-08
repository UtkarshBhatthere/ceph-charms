Overview
========

Ceph is a distributed storage and network file system designed to provide
excellent performance, reliability, and scalability.

This charm deploys additional Ceph OSD storage service units and should be
used in conjunction with the 'ceph' charm to scale out the amount of storage
available in a Ceph cluster.

Usage
=====
       
The charm also supports specification of the storage devices to use in the ceph
cluster::

    osd-devices:
        A list of devices that the charm will attempt to detect, initialise and
        activate as ceph storage.
        
        This this can be a superset of the actual storage devices presented to
        each service unit and can be changed post ceph-osd deployment using
        `juju set`.

For example::        

    ceph-osd:
        osd-devices: /dev/vdb /dev/vdc /dev/vdd /dev/vde
        
Boot things up by using::

    juju deploy -n 3 --config ceph.yaml ceph
    
You can then deploy this charm by simple doing::

    juju deploy -n 10 --config ceph.yaml ceph-osd
    juju add-relation ceph-osd ceph
    
Once the ceph charm has bootstrapped the cluster, it will notify the ceph-osd
charm which will scan for the configured storage devices and add them to the
pool of available storage.

Network Space support
=====================

This charm supports the use of Juju Network Spaces, allowing the charm to be bound to network space configurations managed directly by Juju.  This is only supported with Juju 2.0 and above.

Network traffic can be bound to specific network spaces using the public (front-side) and cluster (back-side) bindings:

    juju deploy ceph-osd --bind "public=data-space cluster=cluster-space"

alternatively these can also be provided as part of a Juju native bundle configuration:

    ceph-osd:
      charm: cs:xenial/ceph-osd
      num_units: 1
      bindings:
        public: data-space
        cluster: cluster-space

Please refer to the [Ceph Network Reference](http://docs.ceph.com/docs/master/rados/configuration/network-config-ref) for details on how using these options effects network traffic within a Ceph deployment.

**NOTE:** Spaces must be configured in the underlying provider prior to attempting to use them.

**NOTE**: Existing deployments using ceph-*-network configuration options will continue to function; these options are preferred over any network space binding provided if set.


Contact Information
===================

Author: James Page <james.page@ubuntu.com>
Report bugs at: http://bugs.launchpad.net/charms/+source/ceph-osd/+filebug
Location: http://jujucharms.com/charms/ceph-osd
