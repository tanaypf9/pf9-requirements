# Copyright (C) 2011 OpenStack, LLC.
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2013 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import collections

from openstack_requirements import project
from openstack_requirements import requirement

from packaging import specifiers


class RequirementsList(object):
    def __init__(self, name, project):
        self.name = name
        self.reqs_by_file = {}
        self.project = project
        self.failed = False

    @property
    def reqs(self):
        return {k: v for d in self.reqs_by_file.values()
                for k, v in d.items()}

    def extract_reqs(self, content, strict):
        reqs = collections.defaultdict(set)
        parsed = requirement.parse(content)
        for name, entries in parsed.items():
            if not name:
                # Comments and other unprocessed lines
                continue
            list_reqs = [r for (r, line) in entries]
            # Strip the comments out before checking if there are duplicates
            list_reqs_stripped = [r._replace(comment='') for r in list_reqs]
            if strict and len(list_reqs_stripped) != len(set(
                    list_reqs_stripped)):
                print("Requirements file has duplicate entries "
                      "for package %s : %r." % (name, list_reqs))
                self.failed = True
            reqs[name].update(list_reqs)
        return reqs

    def process(self, strict=True):
        """Convert the project into ready to use data.

        - an iterable of requirement sets to check
        - each set has the following rules:
          - each has a list of Requirements objects
          - duplicates are not permitted within that list
        """
        print("Checking %(name)s" % {'name': self.name})
        # First, parse.
        for fname, content in self.project.get('requirements', {}).items():
            print("Processing %(fname)s" % {'fname': fname})
            if strict and not content.endswith('\n'):
                print("Requirements file %s does not "
                      "end with a newline." % fname)
            self.reqs_by_file[fname] = self.extract_reqs(content, strict)

        for name, content in project.extras(self.project).items():
            print("Processing .[%(extra)s]" % {'extra': name})
            self.reqs_by_file[name] = self.extract_reqs(content, strict)


def _get_exclusions(req):
    return set(
        spec
        for spec in req.specifiers.split(',')
        if '!=' in spec or '<' in spec
    )


def _is_requirement_in_global_reqs(req, global_reqs):
    req_exclusions = _get_exclusions(req)
    for req2 in global_reqs:

        if (req.package == req2.package and
           req.location == req2.location and
           req.markers == req2.markers and
           req.comment == req2.comment):
            # This matches the right package and other properties, so
            # ensure that any exclusions are a subset of the global
            # set.
            global_exclusions = _get_exclusions(req2)
            if req_exclusions.issubset(global_exclusions):
                return True
            else:
                print(
                    "Requirement for package {} "
                    "has an exclusion not found in the "
                    "global list: {} vs. {}".format(
                        req.package, req_exclusions, global_exclusions)
                )
                return False

    return False


def get_global_reqs(content):
    """Return global_reqs structure.

    Parse content and return dict mapping names to sets of Requirement
    objects."

    """
    global_reqs = {}
    parsed = requirement.parse(content)
    for k, entries in parsed.items():
        # Discard the lines: we don't need them.
        global_reqs[k] = set(r for (r, line) in entries)
    return global_reqs


def _validate_one(name, reqs, branch_reqs, blacklist, global_reqs):
    "Returns True if there is a failure."
    if (name in branch_reqs.reqs and
       reqs == branch_reqs.reqs[name]):
        # Unchanged [or a change that preserves a current value]
        return False
    if name in blacklist:
        # Blacklisted items are not synced and are managed
        # by project teams as they see fit, so no further
        # testing is needed.
        return False
    if name not in global_reqs:
        print("Requirement %s not in openstack/requirements" %
              str(reqs))
        return True
    counts = {}
    for req in reqs:
        if req.extras:
            for extra in req.extras:
                counts[extra] = counts.get(extra, 0) + 1
        else:
            counts[''] = counts.get('', 0) + 1
        if not _is_requirement_in_global_reqs(
                req, global_reqs[name]):
            print("Requirement for package %s : %s does "
                  "not match openstack/requirements value : %s" % (
                      name, str(req), str(global_reqs[name])))
            return True
    for extra, count in counts.items():
        if count != len(global_reqs[name]):
            print("Package %s%s requirement does not match "
                  "number of lines (%d) in "
                  "openstack/requirements" % (
                      name,
                      ('[%s]' % extra) if extra else '',
                      len(global_reqs[name])))
            return True
    return False


def validate(head_reqs, branch_reqs, blacklist, global_reqs):
    failed = False
    # iterate through the changing entries and see if they match the global
    # equivalents we want enforced
    for fname, freqs in head_reqs.reqs_by_file.items():
        print("Validating %(fname)s" % {'fname': fname})
        for name, reqs in freqs.items():
            failed = (
                _validate_one(
                    name,
                    reqs,
                    branch_reqs,
                    blacklist,
                    global_reqs,
                )
                or failed
            )

    return failed


def _find_constraint(req, constraints):
    """Return the constraint matching the markers for req.

    Given a requirement, find the constraint with matching markers.
    If none match, find a constraint without any markers at all.
    Otherwise return None.
    """
    for constraint_setting, _ in constraints:
        if constraint_setting.markers == req.markers:
            return constraint_setting
    # Try looking for a constraint without any markers.
    for constraint_setting, _ in constraints:
        if not constraint_setting.markers:
            return constraint_setting
    return None


def validate_lower_constraints(req_list, constraints, blacklist):
    """Return True if there is an error.

    :param reqs: RequirementsList for the head of the branch
    :param constraints: Parsed lower-constraints.txt or None

    """
    if constraints is None:
        return False

    parsed_constraints = requirement.parse(constraints)

    failed = False

    for fname, freqs in req_list.reqs_by_file.items():

        if fname == 'doc/requirements.txt':
            # Skip things that are not needed for unit or functional
            # tests.
            continue

        print("Validating lower constraints of {}".format(fname))

        for name, reqs in freqs.items():

            if name in blacklist:
                continue

            if name not in parsed_constraints:
                print('Package {!r} is used in {} '
                      'but not in lower-constraints.txt'.format(
                          name, fname))
                failed = True
                continue

            for req in reqs:
                spec = specifiers.SpecifierSet(req.specifiers)
                # FIXME(dhellmann): This will only find constraints
                # where the markers match the requirements list
                # exactly, so we can't do things like use different
                # constrained versions for different versions of
                # python 3 if the requirement range is expressed as
                # python_version>3.0. We can support different
                # versions if there is a different requirement
                # specification for each version of python. I don't
                # really know how smart we want this to be, because
                # I'm not sure we want to support extremely
                # complicated dependency sets.
                constraint_setting = _find_constraint(
                    req,
                    parsed_constraints[name],
                )
                if not constraint_setting:
                    print('Unable to find constraint for {} '
                          'matching {!r} or without any markers.'.format(
                              name, req.markers))
                    failed = True
                    continue
                print('req', req)
                print('constraint_setting', constraint_setting)

                version = constraint_setting.specifiers.lstrip('=')

                if not spec.contains(version):
                    print('Package {!r} is constrained to {} '
                          'which is incompatible with the settings {} '
                          'from {}.'.format(
                              name, version, req, fname))
                    failed = True

                min = [
                    s
                    for s in req.specifiers.split(',')
                    if '>' in s
                ]
                if not min:
                    # No minimum specified. Ignore this and let some
                    # other validation trap the error.
                    continue

                expected = min[0].lstrip('>=')
                if version != expected:
                    print('Package {!r} is constrained to {} '
                          'which does not match '
                          'the minimum version specifier {} in {}'.format(
                              name, version, expected, fname))
                    failed = True
    return failed
