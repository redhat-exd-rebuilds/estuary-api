# SPDX-License-Identifier: GPL-3.0+
from setuptools import find_packages, setup

setup(
    name='estuary',
    version='0.1',
    description='The Estuary API used to query the build to release pipeline',
    author='Red Hat, Inc.',
    author_email='mprahl@redhat.com',
    license='GPLv3+',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'prometheus-client',
        'ldap3',
        'flask-oidc',
        'gunicorn',
        'Flask',
        # Pin the version until this is merged:
        # https://github.com/neo4j-contrib/neomodel/pull/553
        'neomodel==3.3.2',
        'pytz',
        'six',
    ],
    extras_require={
        'auth': ['flask_oidc', 'ldap3'],
    }
)
