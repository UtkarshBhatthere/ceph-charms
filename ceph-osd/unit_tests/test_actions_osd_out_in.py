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

import sys

from test_utils import CharmTestCase

sys.path.append('hooks')

import osd_in_out as actions


class OSDOutTestCase(CharmTestCase):
    def setUp(self):
        super(OSDOutTestCase, self).setUp(
            actions, ["check_call",
                      "get_local_osd_ids",
                      "assess_status"])

    def test_osd_out(self):
        self.get_local_osd_ids.return_value = [5]
        actions.osd_out([])
        cmd = ['ceph', '--id',
               'osd-upgrade', 'osd', 'out', '5']
        self.check_call.assert_called_once_with(cmd)
        self.assess_status.assert_called_once_with()


class OSDInTestCase(CharmTestCase):
    def setUp(self):
        super(OSDInTestCase, self).setUp(
            actions, ["check_call",
                      "get_local_osd_ids",
                      "assess_status"])

    def test_osd_in(self):
        self.get_local_osd_ids.return_value = [5]
        actions.osd_in([])
        cmd = ['ceph', '--id',
               'osd-upgrade', 'osd', 'in', '5']
        self.check_call.assert_called_once_with(cmd)
        self.assess_status.assert_called_once_with()


class MainTestCase(CharmTestCase):
    def setUp(self):
        super(MainTestCase, self).setUp(actions, ["action_fail"])

    def test_invokes_action(self):
        dummy_calls = []

        def dummy_action(args):
            dummy_calls.append(True)

        with mock.patch.dict(actions.ACTIONS, {"foo": dummy_action}):
            actions.main(["foo"])
        self.assertEqual(dummy_calls, [True])

    def test_unknown_action(self):
        """Unknown actions aren't a traceback."""
        exit_string = actions.main(["foo"])
        self.assertEqual("Action foo undefined", exit_string)

    def test_failing_action(self):
        """Actions which traceback trigger action_fail() calls."""
        dummy_calls = []

        self.action_fail.side_effect = dummy_calls.append

        def dummy_action(args):
            raise ValueError("uh oh")

        with mock.patch.dict(actions.ACTIONS, {"foo": dummy_action}):
            actions.main(["foo"])
        self.assertEqual(dummy_calls, ["Action foo failed: uh oh"])
