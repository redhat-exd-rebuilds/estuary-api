# SPDX-License-Identifier: GPL-2.0+
from setuptools import setup, find_packages

setup(
    name='purview',
    version='0.1',
    description='The Purview API used to query the build to release pipeline',
    author='Red Hat, Inc.',
    author_email='mprahl@redhat.com',
    license='GPLv3+',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
)
