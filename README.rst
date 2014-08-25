============================================
 Global Requirements for OpenStack Projects
============================================

Why Global Requirements?
========================
During the Havana release cycle we kept running into coherency issues
with trying to install all the OpenStack components into a single
environment. The issue is that syncing of requirements.txt between
projects was an eventually consistent problem. Some projects would
update quickly, others would not. We'd never have the same versions
specified as requirements between packages.

Because of the way that python package installation with pip works,
this means that if you get lucky you'll end up with a working
system. If you don't you can easily break all of OpenStack on a
requirements update.

An example of how bad this had gotten is that python keystoneclient
would typically be installed / uninstalled 6 times during the course
of a devstack gate run during Havana. If the last version of python
keystoneclient happened to be incompatible with some piece of
OpenStack a very hard to diagnose break occurs.

We also had an issue with projects adding dependencies of python
libraries without thinking through the long term implications of those
libraries. Is the library actively maintained? Is the library of a
compatible license? Is the library duplicative of existing libraries
that we already have in requirements? Is the library python 3
compatible? Is the library something that already exists in Linux
Distros that we target (Ubuntu / Fedora). The answer to many of these
questions was no.

Global requirements gives us a single place where we can evaluate
these things so that we can make a global decision for OpenStack on
the suitability of the library.

Solution
========

The mechanics of the solution is relatively simple. We maintain a
central list of all the requirements (``global-requirements.txt``)
that are allowed in OpenStack projects. This is enforcing for both
``requirements.txt`` and ``test-requirements.txt``.

Enforcement for Test Runs
-------------------------

When installing with devstack, we overwrite the ``requirements.txt``
and ``test-requirements.txt`` for **all** installed projects with the
versions from ``global-requirements.txt``. This ensures that we will
get a deterministic set of requirements installed in the test system,
and it won't be a guessing game based on the last piece of software to
install.

Enforcement in Projects
-----------------------

All projects that have accepted the requirements contract (as listed
in ``projects.txt``) are expected to run a requirements compatibility
job that ensures that they can not change any lines in global
requirements to versions not in ``global-requirements.txt``. It also
ensures that those projects can't add a requirement that's not already
in ``global-requirements.txt``.

Automatic Sync of Accepted Requirements
---------------------------------------

If a new requirement is proposed to OpenStack and accepted to
requirements, the system then also automatically pushes a review
request for the new requirements definition to the projects.

This is intended as a time saving device for projects, as they can
fast approve requirements syncs and not have to manually worry about
whether or not they are up to date with the global definition.

Running
=======

To use this, run:

  python update.py path/to/project

Entries in requirements.txt and test-requirements.txt will have their
versions updated to match the entries listed here. Any entries in the
target project which do not first exist here will be removed. No
entries will be added.

Review Guidelines
=================

There are a set of questions that every reviewer should ask on any
proposed requirements change (and one that proposers should pre answer
to make things go smoother).

General Review Criteria
-----------------------

- No libraries should contain version caps

  As a community we value early feedback of broken upstream
  requirements, so version caps should be avoided except when dealing
  with exceptionally unstable libaries.

  Exceptionally unstable libraries should also be considered something
  we want to replace over time with ones that aren't, or are upstream
  communities where we'd like to encourage getting more testing into
  their normal upstream process.

- Libraries should contain a sensible known working minimum

  Bare library names are bad. If it's unknown what a working minimum
  is, look at the output of pip freeze at the end of a successful
  devstack/tempest run and use that version. At least that's known to
  be working now.

- Commit message referencing which projects want to use this

  And preferably comments about what feature / blueprint requires this
  new library to be added. Ideally the proposed code is up already in
  the projects so that it's use can be seen.

For new Requirements
--------------------

- Is the library actively maintained?

  We *really* want some indication that the library is something we
  can get support on if we or our users find a bug, and that we
  don't have to take over and fork the library.

  Pointers to recent activity upstream and a consistent release model
  appreciated.

- Is the library good code?

  It's expected before just telling everyone to download arbitrary 3rd
  party code from the internet the submitter has taken a deep dive
  into the code to get a feel on whether this code seems solid enough
  to depend on. That includes ensuring the upstream code has some
  reasonable testing baked in.

- Is the library python 3 compatible?

  OpenStack will eventually need to support python 3. At this point
  adding non python 3 compatible libraries should only be done under
  *extreme* need. It should be considered a very big exception.

- Is the library license compatible?

  Preferably Apache2, BSD, MIT licensed. LGPL is ok. GPL or AGPL is
  verboten. Any other oddball license should be rejected.

- Is the library already packaged in the distros we target (Ubuntu
  latest / Fedora latest)?

  By adding something to OpenStack ``global-requirements.txt`` we are
  basically demanding that Linux Distros package this for the next
  release of OpenStack. If they already have, great. If not, we should
  be cautious adding it. :ref:`finding-distro-status`

- Is the function of this library already covered by other libraries
  in global-requirements?

  Everyone has their own pet libraries they like to use, but we do not
  need 3 different request mocking libraries in OpenStack.

  If this new requirement is about replacing an existing library with
  one that's better suited for our needs then we also need the
  transition plan to drop the old library in a reasonable amount of
  time.

For Upgrading Requirements Versions
-----------------------------------

- Why is it impossible to use the current version definition?

  Everyone likes everyone else to use the latest version of their
  code, however deployers really don't like to be constantly updating
  things. Unless it's actually **impossible** to use the minimum
  version specified in ``global-requirements.txt`` it should not be
  changed.

  Leave that decision to deployers and distros.

.. _finding-distro-status:

Finding Distro Status
---------------------

The OpenStack distro support policy is that new software should be
written to support the latest Ubuntu and Fedora releases, with support
of the last LTS of those distros a bonus.  We would also like to
ensure that there is not too much pain for the Debian and SuSE
communities.

For people unfamiliar with Linux Distro packaging you can use the
following tools to search for packages:

 - Ubuntu - http://packages.ubuntu.com/
 - Fedora - https://apps.fedoraproject.org/packages/
