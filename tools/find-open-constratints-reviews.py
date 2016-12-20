#!/usr/bin/env python

from __future__ import print_function

import argparse
import collections
import json
import requests
import requests.auth
import urllib
import sys


def get_reviews(host, query):
    print('Running: %s' % (query), file=sys.stderr)
    url = ('https://%s/changes/?q=%s&o=CURRENT_REVISION'
           % (host, urllib.quote_plus(query, safe='/:=><')))
    r = requests.get(url)
    if r.status_code == 200:
        data = json.loads(r.text[4:])
    else:
        data = []
    return data


def main(args):
    for change in get_reviews('review.openstack.org', args.query):
        if change['project'] == 'openstack/ceilometer':
            continue
        print("%(project)s\t%(_number)s" % change)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vote-a-tron')

    parser.add_argument('--query', dest='query', required=True,
                        help=('Gerrit query matching *ALL* reviews to '
                              'vote on'))
    # FIXME(tonyb): take the fields as an argument to make this more flexible

    args, extras = parser.parse_known_args()

    sys.exit(main(args))
