# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from packaging import specifiers


def check_compatible(global_reqs, constraints):
    """Check compatibility between requirements and constraints.

    A change to global-requirements that wants to make changes
    incompatible with the current frozen constraints needs to also raise
    those constraints.
    Load global-requirements
    Load upper-constraints.txt
    Check that every version within upper-constraints.txt is either
    A) Missing from global-requirements - its a transitive dep or
       a removed dep.
    B) Compatible with any of the versions in global-requirements.
       This is not-quite right, because we should in principle match
       markers, but that requires evaluating the markers which we
       haven't yet implemented. Being compatible with one of the
       requirements is good enough proxy to catch most cases.

    :param global_reqs: A set of global requirements after parsing.
    :param constraints: The same from upper-constraints.txt.
    :return: A list of the parsed package tuples that failed.
    """

    def satisfied(reqs, name, version, failures):
        if name not in reqs:
            return True
        tested = []
        for constraint, _ in reqs[name]:
            spec = specifiers.SpecifierSet(constraint.specifiers)
            if spec.contains(version):
                return True
            tested.append(constraint.specifiers)
        failures.append('Constraint for %s==%s does not match requirement %s' %
                        (name, version, tested))
        return False
    failures = []
    for pkg_constraints in constraints.values():
        for constraint, _ in pkg_constraints:
            name = constraint.package
            version = constraint.specifiers[3:]
            satisfied(global_reqs, name, version, failures)
    return failures
