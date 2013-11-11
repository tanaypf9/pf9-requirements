Requirements Commandments
=========================

In order to add or change the Python dependency requirements of an Openstack
project, it must first be added to the requirements repository.

Add the requirements to the global-requirements.txt and test-requirements.txt.

The requirement specification should usually include both a lower and upper
bound. The lower bound should reflect the oldest known version of the package
which has the APIs required. An upper bound should be added based on a package's
policy of release versioning with respect to incompatible API changes so that
we avoid problems caused by a future incompatible release.

Once the change to openstack/requirements has merged, the local pypi mirror
will be updated and then the requirements file for the OpenStack project may
be updated. The new requirement specification must match exactly what is in
openstack/requirements.

Review Criteria
===============

* License

  Apache2, MIT, BSD are probably okay, (Copyleft licenses may be okay depending
  on circumstances)

* Python3 compatibility

  Openstack is slowly moving towards python3 compatibility so new dependencies
  should be python3 compatible.

* Active development

  Dependencies that are not actively maintained cause headaches and are frowned
  upon for inclusion in the requirements project.

* prefer items already packaged in distros

  It's preferable to have python dependencies already packaged by the major
  consumers of Openstack. This includes Ubuntu/Debian/Fedora/RHEL/SUSE.

* project has api compat commitment/policy

  It is also preferable that the API between the same python depenedency
  versions is compatible.

* Project has a reasonable security history (Open and Closed CVEs)

  It is desirable to check the security history before accepting any additonal
  python requirements. Please check the dependancy against:

  http://cve.mitre.org/cve/cve.html

  or

  http://secunia.com/advisories/search/

* Commit log message includes reasoning for update

   Ensure that the commit log message includes information about the OpenStack
   project(s) using the requirements.
