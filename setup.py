#!/usr/bin/env python
# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from distutils import log
from distutils.command.build_clib import build_clib
import multiprocessing
import os
import subprocess
import sys

import setuptools
from setuptools.command.build_ext import build_ext


CFFI_REQ = 'cffi>=1.7,!=1.11.3'
INSTALL_REQS = []
SETUP_REQS = ['wheel']
if '_cffi_backend' not in sys.builtin_module_names:
    INSTALL_REQS.append(CFFI_REQ)
    SETUP_REQS.append(CFFI_REQ)
HERE = os.path.abspath(os.path.dirname(__file__))
CLIB_PREFIX = os.path.join(HERE, 'build', 'clib')


class BuildCLib(build_clib):

    def run(self):
        if not self.libraries:
            return
        log.info('Building libyang C library ...')
        if not os.path.exists(CLIB_PREFIX):
            os.makedirs(CLIB_PREFIX)
        commands = [
            [
                'cmake', os.path.join(HERE, 'clib'),
                '-DCMAKE_BUILD_TYPE=release',
                '-DENABLE_STATIC=ON',
                '-DCMAKE_C_FLAGS=-fPIC',
                '-DENABLE_BUILD_TESTS=OFF',
                '-DENABLE_VALGRIND_TESTS=OFF',
                '-DCMAKE_INSTALL_PREFIX=%s' % CLIB_PREFIX,
                '-DGEN_LANGUAGE_BINDINGS=0',
            ],
            ['make', '-j%d' % multiprocessing.cpu_count()],
            ['make', 'install'],
        ]
        for cmd in commands:
            log.debug('%s$ %s', CLIB_PREFIX, ' '.join(cmd))
            subprocess.check_call(cmd, cwd=CLIB_PREFIX)

    def get_library_names(self):
        if not self.libraries:
            return []
        return ['pcre', 'metadata', 'yangdata', 'nacm', 'user_date_and_time']


class BuildExt(build_ext):

    def run(self):
        if self.distribution.has_c_libraries():
            self.include_dirs.append(os.path.join(CLIB_PREFIX, 'include'))
            self.library_dirs.append(CLIB_PREFIX)
        return build_ext.run(self)


LIBRARIES = []
if os.environ.get('LIBYANG_INSTALL') != 'system':
    LIBRARIES.append(('yang', {'sources': ['clib']}))


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(name='yangvoodoo',
                 # CHANGE VERSION NUMBER HERE
                 version='0.0.5-devel', author='Adam Allen',
                 author_email='allena29@users.noreply.github.com',
                 description='Python based access to YANG Datatstores',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 url='http://github.com/allena29/pyyang-voodoo',
                 packages=['yangvoodoo'],
                 install_requires=[
                     'libyang',
                     'cffi',
                     'jinja2',
                     'lxml',
                     'dictdiffer',
                 ],
                 zip_safe=False,
                 include_package_data=True,

                 classifiers=['Programming Language :: Python :: 3',
                              'License :: OSI Approved :: Apache License 2.0',
                              'Operating System :: OS Independent'])
