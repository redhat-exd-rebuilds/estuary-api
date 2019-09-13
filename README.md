[![Build Status](https://travis-ci.org/release-engineering/estuary-api.svg?branch=master)](https://travis-ci.org/release-engineering/estuary-api)
[![Docs Status](https://readthedocs.org/projects/estuary-api/badge/?version=latest)](https://estuary-api.readthedocs.io/en/latest/?badge=latest)

# Getting Started

## Overview

Estuary visualizes the story an artifact takes in the Red Hat build to release pipeline,
with a focus on the automation of container rebuilds due to CVEs. This repository contains
the API and scrapers for the [Estuary front end](https://github.com/release-engineering/estuary).

## Development

To setup a development environment:
* Create and activate a [Python virtual environment](https://virtualenv.pypa.io/en/stable/)
    (Python 3 is preferred)
* Install the API and its dependencies with:
  ```bash
  $ python setup.py develop
  ```
* (Optional): Install the scrapers' dependencies with:
  ```bash
  $ pip install -r scraper-requirements.txt
  ```

To start the development web server, run:

```bash
$ scripts/run-flask.sh
```


## Run the Unit Tests

Since the unit tests require a running Neo4j instance, the tests are run in Docker containers using
Docker Compose. The commands required to run the unit tests are abstracted in
`scripts/run-tests.sh`. This script will create the Docker image required to run the tests based
on `docker/Dockerfile-tests`, create a container with Neo4j, create another container to run
the tests based on the built Docker image, run the tests, and then delete the two created
containers.

To install Docker and Docker Compose on Fedora, run:

```bash
$ sudo dnf install docker docker-compose
```

To start Docker, run:

```bash
$ sudo systemctl start docker
```

To run the tests, run:

```bash
$ sudo scripts/run-tests.sh
```

To run just a single test, you can run:

```bash
sudo scripts/run-tests.sh pytest-3 -vvv tests/test_file::test_name
```

## Code Styling

The codebase conforms to the style enforced by `flake8` with the following exceptions:
* The maximum line length allowed is 100 characters instead of 80 characters

In addition to `flake8`, docstrings are also enforced by the plugin `flake8-docstrings` with
the following exemptions:
* D100: Missing docstring in public module
* D104: Missing docstring in public package

The format of the docstrings should be in the Sphynx style such as:

```
Get a resource from Neo4j.

:param str resource: a resource name that maps to a neomodel class
:param str uid: the value of the UniqueIdProperty to query with
:return: a Flask JSON response
:rtype: flask.Response
:raises NotFound: if the item is not found
:raises ValidationError: if an invalid resource was requested
```

## Code Documentation
To document new files, please check [here](https://github.com/release-engineering/estuary-api/tree/master/docs).


## Authorization

If authentication is enabled, Estuary can authorize users based on their employee type and a user
whitelist configured through the membership of an LDAP group.

### Employee Type

You may set the list of valid employee types with the configuration item `EMPLOYEE_TYPES`. These
employee types map to the `employeeType` LDAP attribute of the user that is added to the OpenID
Connect token received by Estuary.

### Configuring the Whitelist

To configure a whitelist of users, they must be part of an LDAP group configured with Estuary. The
following configuration items are required:

* `LDAP_URI` - the URI to the LDAP server to connect to in the format of
    `ldaps://server.domain.local`.
* `LDAP_EXCEPTIONS_GROUP_DN` - the distinguished name to the LDAP group acting as the whitelist.

The following configuration items are optional:

* `LDAP_CA_CERTIFICATE` - the path to the CA certificate that signed the certificate used by the
    LDAP server. This only applies if you are using LDAPS. This defaults to
    `/etc/pki/tls/certs/ca-bundle.crt`.
* `LDAP_GROUP_MEMBERSHIP_ATTRIBUTE` - the LDAP attribute that represents a user in the group. This
    defaults to `uniqueMember`.
