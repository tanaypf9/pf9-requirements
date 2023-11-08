#!/usr/bin/env bash


declare -a ubuntu_focal=(3.8 3.9)
declare -a ubuntu_jammy=(3.10 3.11)

for container in ubuntu-{focal,jammy} ; do
    declare dist=${container//ubuntu-}
    declare -a pyvers=($(eval echo \${${container/-/_}[*]}))
    declare -a pkgs=(
        build-essential git python3-all python3-pip python3-all-dev python3-venv tox
    )

    echo $container $dist ${pyvers[@]}

    for pyver in "${pyvers[@]}" ; do
        pkgs+=(python${pyver} python${pyver}-venv python${pyver}-dev)
    done

    # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    #     bash -c "apt-get update && apt-get dist-upgrade --yes" &&\
    # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    #     bash -c "apt-get install --yes ${pkgs[@]}" &&\
    # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    #     bash -c "pip3 install bindep"

    bindep_fallback='/home/zuul/src/opendev.org/openstack/requirements/Containerfiles/bindep-fallback.txt'
    pkgs=($(podman exec --interactive --tty --user root --env TERM=$TERM $container bash -c "bindep -f ${bindep_fallback} --list_all newline compile test | grep -v pypy" | tr -d '[\r]'))
    pkgs+=(libkrb5-dev libnss3-dev libsystemd-dev liberasurecode-dev libpcre3-dev)
    podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
        bash -c "apt-get install --yes ${pkgs[*]}"

    # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    #     bash -c "pip3 install bindep" && \
    # # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    # #     bash -c 'echo $(bindep -f /home/zuul/src/opendev.org/openstack/requirements/Containerfiles/bindep-fallback.txt --list_all newline compile test | grep -v pypy)'
    # # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    # #     bash -c 'echo $(bindep -f /home/zuul/src/opendev.org/openstack/requirements/Containerfiles/bindep-fallback.txt -b compile test | grep -v pypy)'
    # podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
    #     bash -c 'apt-get install --yes --fix-missing --fix-broken $(bindep -f /home/zuul/src/opendev.org/openstack/requirements/Containerfiles/bindep-fallback.txt -b compile test | grep -v pypy) libkrb5-dev libnss3-dev libsystemd-dev liberasurecode-dev libpcre3-dev'
    podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
        bash -c "> /var/lib/dpkg/info/mysql-server-8.0.postinst; dpkg --configure -a"
    podman exec --interactive --tty --user root --env TERM=$TERM --env DEBIAN_FRONTEND=noninteractive $container \
        bash -c "apt-get install -y"

    for pyver in "${pyvers[@]}" ; do
        echo $container $dist $pyver
        toxdir=".tox-${dist}-${pyver}"
        workdir=/home/zuul/src/opendev.org/openstack/requirements
        podman exec --interactive --tty --user zuul --workdir $workdir --env TERM=$TERM $container \
            bash -c "tox --workdir ${toxdir} --override basepython=python${pyver} --discover /usr/bin/python${pyver} --colored=no  --notest -re venv" &&\
        podman exec --interactive --tty --user zuul --workdir $workdir --env TERM=$TERM $container \
            bash -c "${toxdir}/venv/bin/generate-constraints -b blacklist.txt -r global-requirements.txt -p python${pyver} > ${dist}-${pyver}-upper-constraints.txt"
    done
done

# https://github.com/pypa/pip/issues/4022
# https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1635463
tox -re venv --notest
.tox/venv/bin/merge-constraints --blacklist blacklist.txt \
    --constraints 3.8:focal-3.8-upper-constraints.txt \
    --constraints 3.9:focal-3.9-upper-constraints.txt \
    --constraints 3.10:jammy-3.10-upper-constraints.txt \
    --constraints 3.11:jammy-3.11-upper-constraints.txt \
        | grep -v pkg_resources > upper-constraints.txt
