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

import testtools

from openstack_requirements import constraints
from openstack_requirements import requirement


class TestCheckCompatible(testtools.TestCase):

    def test_non_requirement(self):
        global_reqs = {}
        good_constraints = requirement.parse("foo===1.2.5\n")
        self.assertEqual(
            [],
            constraints.check_compatible(global_reqs, good_constraints)
        )

    def test_compatible(self):
        global_reqs = requirement.parse("foo>=1.2\nbar>2.0\n")
        good_constraints = requirement.parse("foo===1.2.5\n")
        self.assertEqual(
            [],
            constraints.check_compatible(global_reqs, good_constraints)
        )

    def test_constraint_below_range(self):
        global_reqs = requirement.parse("oslo.concurrency>=2.3.0\nbar>1.0\n")
        bad_constraints = requirement.parse("oslo.concurrency===2.2.0\n")
        results = constraints.check_compatible(global_reqs, bad_constraints)
        self.assertNotEqual([], results)

    def test_constraint_above_range(self):
        global_reqs = requirement.parse("foo>=1.2,<2.0\nbar>1.0\n")
        bad_constraints = requirement.parse("foo===2.0.1\n")
        results = constraints.check_compatible(global_reqs, bad_constraints)
        self.assertNotEqual([], results)
