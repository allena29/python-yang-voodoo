FROM alpine:3.10.0

RUN apk add python3

RUN apk add git cmake swig python3-dev libxml2-dev libtool \
            py3-setuptools readline-dev libxslt-dev make \
            protobuf-c-dev libev-dev openssl-dev \
            boost-thread libffi-dev bison automake zlib-dev \
            gcc g++ flex pcre-dev alpine-sdk vim musl-dev screen \
            redis

RUN mkdir /opt/dev
WORKDIR /opt/dev

RUN \
      git clone https://github.com/CESNET/libyang.git && \
      git clone https://github.com/sysrepo/libredblack.git && \
      git clone https://github.com/sysrepo/sysrepo.git && \
      git clone https://git.libssh.org/projects/libssh.git libssh  && \
      git clone https://github.com/CESNET/libnetconf2.git && \
      git clone https://github.com/CESNET/Netopeer2.git

RUN \
      cd /opt/dev && \
      git clone https://github.com/allena29/libyang-cffi.git && \
      git clone https://github.com/allena29/python-yang-voodoo.git /working && \
      cd /working && \
      pip3 install -r requirements.txt && \
      pip3 install redis

# libyang
RUN \
      cd /opt/dev && \
      cd libyang && \
      git checkout v1.0-r3 && \
      mkdir build && cd build && \
      cmake .. && \
      make -j6  && \
      make install && \
      ln -s /usr/local/lib64/*yang* /usr/local/lib

RUN \
      cd /working && \
      git checkout devel && \
      LIBYANG_INSTALL=system python3 setup.py install
RUN \
      cd /opt/dev && \
      cd libyang-cffi && \
      echo "#!/bin/bash" >rebuild.sh && \
      LIBYANG_INSTALL=system python3 setup.py install

RUN \
      cd /opt/dev/libredblack && \
      ./configure && \
      make && \
      make install

RUN \
      cd /opt/dev/sysrepo && \
      git checkout v0.7.8 && \
      mkdir build_python3 && \
      cd build_python3 && \
      cmake -DREPOSITORY_LOC=/sysrepo -DGEN_PYTHON_VERSION=3 .. && \
      make -j6 && \
      make install && \
      ln -s /usr/local/lib64/*ysrepo* /usr/local/lib
