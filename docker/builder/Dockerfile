FROM ubuntu:disco


RUN \
      apt-get update && apt-get install -y \
      # general tools
      git \
      vim \
      curl \
      gnupg \
      apt-transport-https \
      python3 \
      python3-pip

RUN \
      apt-get update && apt-get install -y \
      cmake \
      build-essential \
      supervisor \
      libpcre3-dev \
      pkg-config \
      libavl-dev \
      libev-dev \
      libprotobuf-c-dev \
      protobuf-c-compiler \
      libssl-dev \
      swig \
      python-dev \
      python3-dev \
      libcurl4-openssl-dev \
      libxslt-dev \
      libxml2-dev \
      libtool \
      libtool-bin \
      python-setuptools \
      libreadline-dev \
      python-libxml2 \
      libprotobuf-dev && \
      apt-get install -y libtool libtool-bin libxml2-dev libxslt1-dev libcurl4-openssl-dev xsltproc python-setuptools cmake zlib1g-dev libssl-dev pkg-config libreadline-dev && \
      apt-get install -y bison libboost-thread-dev libboost-thread1.67-dev autoconf automake screen && \
      apt-get install -y libffi-dev || echo 'livffi-dev does not exist'

RUN \
    pip3 install ipython ncclient && \
    mkdir -p /root/.ipython/profile_default   && \
    echo "c.Completer.use_jedi = False" >/root/.ipython/profile_default/ipython_config.py && \
    echo "c.TerminalInteractiveShell.confirm_exit = False" >>/root/.ipython/profile_default/ipython_config.py

# add netconf user
RUN \
    adduser --system netconf && \
    echo "netconf:netconf" | chpasswd

# generate ssh keys for netconf user
RUN \
    mkdir -p /home/netconf/.ssh && \
    ssh-keygen -A && \
    ssh-keygen -t dsa -P '' -f /home/netconf/.ssh/id_dsa && \
    cat /home/netconf/.ssh/id_dsa.pub > /home/netconf/.ssh/authorized_keys

# use /opt/dev as working directory
RUN mkdir /opt/dev
WORKDIR /opt/dev

# libyang
RUN \
      cd /opt/dev && \
      git clone https://github.com/CESNET/libyang.git && \
      cd libyang && \
      git checkout 85d09f3bdf5ea01ea2e01deb384b2b0dde057e3f && \
      git checkout v0.16-r3 && \
      mkdir build && cd build && \
      # We may not end up using these bindings (yang) and instead use (libyang - see below)
      # But it's useful to debug with both
      #cmake -DGEN_LANGUAGE_BINDINGS=ON -DGEN_PYTHON_BINDINGS=ON .. && \
      cmake .. && \
      make -j6  && \
      make install && \
      ldconfig



# sysrepo
RUN \
      cd /opt/dev && \
      git clone https://github.com/sysrepo/sysrepo.git && \
      cd sysrepo && \
      # git checkout 724a62fa830df7fcb2736b1ec41b320abe5064d2 && \
      git checkout v0.7.7 && \
      mkdir build_python3 && \
      cd build_python3 && \
      cmake -DREPOSITORY_LOC=/sysrepo -DGEN_PYTHON_VERSION=3 .. && \
      make -j6 && \
      make install && \
      ldconfig

RUN \
      git clone https://github.com/allena29/libyang-cffi.git && \
      cd libyang-cffi && \
      echo "#!/bin/bash" >rebuild.sh && \
      LIBYANG_INSTALL=system python3 setup.py install


RUN \
      cd / && \
      git clone https://github.com/allena29/python-yang-voodoo.git working && \
      cd working && \
      # git checkout  context-and-logging && \
      echo "v0.0.2-devel-stub" && \
      cd /working && \
      pip3 install -r requirements.txt && \
      python3 setup.py install


# libssh
RUN \
      cd /opt/dev && \
      git clone https://git.libssh.org/projects/libssh.git libssh && \
      cd libssh && \
      # git checkout afa4021ded6e58da4ee4d01dbf4e503d3711d002 && \
      git checkout libssh-0.8.7 && \
      mkdir build && cd build && \
      cmake .. && \
      make -j6 && \
      make install && \
      ldconfig

# libnetconf2
RUN \
      git clone https://github.com/CESNET/libnetconf2.git && \
      cd libnetconf2 && mkdir build && cd build && \
      # git checkout 54ba1c7a1dbd85f3e700c1629ced8e4b52bac4ec && \
      git checkout v0.12-r1 && \
      cmake .. && \
      make -j6 && \
      make install && \
      ldconfig

# keystore
RUN \
      cd /opt/dev && \
      git clone https://github.com/CESNET/Netopeer2.git && \
      cd Netopeer2 && \
      # git checkout d3ae5423847cbfc67c844ad19288744701bd47a4 && \
      git checkout v0.7-r1 && \
      # This commit fixes keystored method signature (original-xpath missing)
      git checkout 6db56863fcac3fc21c18835576314a75ceea1267 && \
      cd keystored && mkdir build && cd build && \
      cmake .. && \
      make -j6  && \
      make install && \
      ldconfig

# netopeer2
RUN \
      cd /opt/dev && \
      cd Netopeer2/server && mkdir build && cd build && \
      #git checkout d3ae5423847cbfc67c844ad19288744701bd47a4 && \
      git checkout v0.7-r1 && \
      cmake .. && \
      make -j6 && \
      make install && \
      cd ../../cli && mkdir build && cd build && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" .. && \
      make  && \
      make install


ENV MY_VERSION=0.0.2cffi
ENV MY_ARCH=amd64

# Optional build a deb
RUN \
      mkdir ~/sysrepo-python-bundle && \
      cd / && \
      # This isn't right - check compiler options for sysrepo
      tar cvpf /tmp/working.tar /usr/local /sysrepo /usr/lib/x86_64-linux-gnu/libpython3.7*  /usr/lib/python3/dist-packages/*sysrepo* && \
      cd ~/sysrepo-python-bundle && \
      tar xvf /tmp/working.tar && \
      rm -fr usr/local/games && \
      rm -fr usr/local/lib/python2.7 && \
      tar cvpf /tmp/libyang.tar usr/local/lib/python3.7/dist-packages/*libyang* usr/local/lib/python3.7/dist-packages/*yangvoodoo* && \
      tar xvf /tmp/libyang.tar && \
      mkdir ~/sysrepo-python-bundle/DEBIAN && \
      echo "Package: python-yang-vooodoo-bundle" >~/sysrepo-python-bundle/DEBIAN/control && \
      echo "Version: ${MY_VERSION}" >>~/sysrepo-python-bundle/DEBIAN/control && \
      echo "Architecture: ${MY_ARCH}" >>~/sysrepo-python-bundle/DEBIAN/control && \
      echo "Depends: libev4,libprotobuf-c1" >>~/sysrepo-python-bundle/DEBIAN/control && \
      echo "Maintainer: allena29@noreply.user.github.com" >>~/sysrepo-python-bundle/DEBIAN/control && \
      echo "Description: sysrepo/libyang-python bundle without netconf support for local use." >>~/sysrepo-python-bundle/DEBIAN/control && \
      echo "#!/bin/sh" >~/sysrepo-python-bundle/DEBIAN/postinst && \
      echo "ldconfig" >>~/sysrepo-python-bundle/DEBIAN/postinst && \
      echo "touch /tmp/pkginstall" >>~/sysrepo-python-bundle/DEBIAN/postinst && \
      chmod 755 ~/sysrepo-python-bundle/DEBIAN/postinst && \
      dpkg --build ~/sysrepo-python-bundle && \
      mkdir /artefacts && \
      mv /root/sysrepo-python-bundle.deb /artefacts/python-yang-vooodoo_bundle.${MY_VERSION}.${MY_ARCH}.deb



RUN \
    pip3 install mock coverage nose2 autopep8 pyflakes dictdiffer flask && \
    cd /working && \
    echo "Git Pull (v2)" && \
    git config --global user.email "docker-user@localhost" && \
    git pull

RUN \
    touch /builder
ENV EDITOR vim
EXPOSE 830
STOPSIGNAL SIGTERM
WORKDIR /working
