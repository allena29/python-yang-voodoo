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
      screen

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
      python3 /get-pip.py && \
      rm -f /get-pip.py && \
      pip3 install mock coverage nose2 autopep8  && \
      pip3 install lxml jinja2 dictdiffer flask



EXPOSE 830 5000
STOPSIGNAL SIGTERM
WORKDIR /working
CMD /working/start-in-docker.sh
