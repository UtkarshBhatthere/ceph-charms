# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import test_utils

from mock import patch

with patch('charmhelpers.contrib.hardening.harden.harden') as mock_dec:
    mock_dec.side_effect = (lambda *dargs, **dkwargs: lambda f:
                            lambda *args, **kwargs: f(*args, **kwargs))
    import ceph_hooks as hooks

TO_PATCH = [
    'status_set',
    'config',
    'ceph',
    'relation_ids',
    'relation_get',
    'related_units',
    'get_conf',
    'application_version_set',
    'get_upstream_version',
]

CEPH_MONS = [
    'ceph/0',
    'ceph/1',
    'ceph/2',
]


class ServiceStatusTestCase(test_utils.CharmTestCase):

    def setUp(self):
        super(ServiceStatusTestCase, self).setUp(hooks, TO_PATCH)
        self.config.side_effect = self.test_config.get
        self.get_upstream_version.return_value = '10.2.2'

    def test_assess_status_no_monitor_relation(self):
        self.relation_ids.return_value = []
        hooks.assess_status()
        self.status_set.assert_called_with('blocked', mock.ANY)
        self.application_version_set.assert_called_with('10.2.2')

    def test_assess_status_monitor_relation_incomplete(self):
        self.relation_ids.return_value = ['mon:1']
        self.related_units.return_value = CEPH_MONS
        self.get_conf.return_value = None
        hooks.assess_status()
        self.status_set.assert_called_with('waiting', mock.ANY)
        self.application_version_set.assert_called_with('10.2.2')

    def test_assess_status_monitor_complete_no_disks(self):
        self.relation_ids.return_value = ['mon:1']
        self.related_units.return_value = CEPH_MONS
        self.get_conf.return_value = 'monitor-bootstrap-key'
        self.ceph.get_running_osds.return_value = []
        hooks.assess_status()
        self.status_set.assert_called_with('blocked', mock.ANY)
        self.application_version_set.assert_called_with('10.2.2')

    def test_assess_status_monitor_complete_disks(self):
        self.relation_ids.return_value = ['mon:1']
        self.related_units.return_value = CEPH_MONS
        self.get_conf.return_value = 'monitor-bootstrap-key'
        self.ceph.get_running_osds.return_value = ['12345',
                                                   '67890']
        hooks.assess_status()
        self.status_set.assert_called_with('active', mock.ANY)
        self.application_version_set.assert_called_with('10.2.2')
