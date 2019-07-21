FROM ubuntu:disco

# See the builder directory which compiles our dependencies from scratch.
# This is trying to build a minimal file and will just install those packages.

RUN \
      apt-get update && apt-get install -y \
      python3 \
      libprotobuf-c1 \
      libev4 \
      libavl1 \
      curl \
      git \
      openssh-client \
      python3-distutils \
      screen \
      libpython3.7 \
      redis

RUN \
    mkdir -p /root/.ipython/profile_default   && \
    echo "c.Completer.use_jedi = False" >/root/.ipython/profile_default/ipython_config.py && \
    echo "c.TerminalInteractiveShell.confirm_exit = False" >>/root/.ipython/profile_default/ipython_config.py && \
    adduser --system netconf && \
    echo "netconf:netconf" | chpasswd && \
    mkdir -p /home/netconf/.ssh && \
    ssh-keygen -A && \
    ssh-keygen -t dsa -P '' -f /home/netconf/.ssh/id_dsa && \
    cat /home/netconf/.ssh/id_dsa.pub > /home/netconf/.ssh/authorized_keys

ADD artefacts /

RUN \
      dpkg -i /*bundle*.deb && \
      rm -fr /*.deb && \
      apt-get clean && \
      apt-get autoclean


RUN \
      python3 /get-pip.py && \
      rm -f /get-pip.py && \
      pip3 install lxml jinja2 dictdiffer six asn1crypto redis

RUN \
    cd /working && \
    git checkout devel && \
    echo -n "Build Date:" >.buildinfo && \
    date >>.buildinfo && \
    echo "Sysrepo: Commit 660552222ee6376efa560d9bcc7b832886ff460a" >>.buildinfo && \
    echo "Libyang: 1.0r2" >>.buildinfo && \
    echo -n "YangVoodoo:" >>.buildinfo && \
    git log | head -n 1 >>.buildinfo && \
    python3 setup.py install

RUN \
      pip3 install mock coverage nose2 autopep8 pyflakes xenon coveralls pudb


EXPOSE 830 5000
STOPSIGNAL SIGTERM
WORKDIR /working
CMD /working/start-in-docker.sh
