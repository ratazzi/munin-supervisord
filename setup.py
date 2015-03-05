#!/usr/bin/env python
# encoding=utf-8

import errno
import os
import pkgutil
import shutil
import glob
from setuptools.command.install import install as _install
from setuptools import setup, find_packages

PYMUNIN_SCRIPT_FILENAME_PREFIX = u'munin'
PYMUNIN_PLUGIN_DIR = u'./share/munin/plugins'
plugin_names = ['supervisord_process']


class install(_install):
    "Extend base install class to provide a post-install step."

    def run(self):
        if 'MUNIN_PLUGIN_DIR' in os.environ:
            munin_plugin_dir = os.environ.get('MUNIN_PLUGIN_DIR')
        elif self.root is None:
            munin_plugin_dir = os.path.normpath(\
                                                os.path.join(self.prefix, PYMUNIN_PLUGIN_DIR))
        else:
            munin_plugin_dir = os.path.normpath(\
                                                os.path.join(self.root,
                                                             os.path.relpath(self.prefix, '/'),\
                                                             PYMUNIN_PLUGIN_DIR))
        _install.run(self)
        # Installing the plugins requires write permission to plugins directory
        # (/usr/share/munin/plugins) which is default owned by root.
        print "Munin Plugin Directory: %s" % munin_plugin_dir
        if os.path.exists(munin_plugin_dir):
            try:
                for name in plugin_names:
                    source = os.path.join(
                        self.install_scripts,
                        u'%s-%s' % (PYMUNIN_SCRIPT_FILENAME_PREFIX, name)
                    )
                    destination = os.path.join(munin_plugin_dir, name)
                    print "Installing %s to %s." % (name, munin_plugin_dir)
                    shutil.copy(source, destination)
            except IOError, e:
                import traceback
                traceback.print_exc()
                if e.errno in (errno.EACCES, errno.ENOENT):
                    # Access denied or file/directory not found.
                    print "*" * 78
                    if e.errno == errno.EACCES:
                        print ("You do not have permission to install the plugins to %s."
                               % munin_plugin_dir)
                    if e.errno == errno.ENOENT:
                        print ("Failed installing the plugins to %s. "
                               "File or directory not found." % munin_plugin_dir)
                    script = os.path.join(self.install_scripts, 'pymunin-install')
                    f = open(script, 'w')
                    try:
                        f.write('#!/bin/sh\n')
                        for name in plugin_names:
                            source = os.path.join(
                                self.install_scripts,
                                u'%s-%s' % (PYMUNIN_SCRIPT_FILENAME_PREFIX, name)
                            )
                            destination = os.path.join(munin_plugin_dir, name)
                            f.write('cp %s %s\n' % (source, destination))
                    finally:
                        f.close()
                    os.chmod(script, 0755)
                    print ("You will need to copy manually using the script: %s\n"
                           "Example: sudo %s"
                           % (script, script))
                    print "*" * 78
                else:
                    # Raise original exception
                    raise

setup(
    cmdclass={'install': install},
    name='munin-supervisord',
    version='0.0.1',
    author='ratazzi',
    author_email='ratazzi.potts@gmail.com',
    url='https://github.com/ratazzi/munin-supervisord',
    packages=find_packages(),
    description='Munin plugin for Supervisord',
    entry_points={
        'console_scripts': [
            'munin-supervisord_process=munin_supervisord.processes:main',
        ],
    },
    install_requires=[
        'pymunin',
        'psutil',
        'supervisor',
    ],
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
