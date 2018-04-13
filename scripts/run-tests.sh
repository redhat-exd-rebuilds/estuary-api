#!/usr/bin/env bash
# This script runs the test suite using Docker and Docker Compose

for dir in purview tests; do
    find ${dir} -type f \( -name '*.pyc' -or -name '*.pyc' \) -exec rm -f {} \;
done

docker-compose -f docker/docker-compose-tests.yml up -d neo4j
if [ "$1" != "" ]; then
    # The user passed at least one argument, so use those arguments as the run command instead
    # of the default
    docker-compose -f docker/docker-compose-tests.yml run --rm tests sh -c "while ! nc -z -w 2 neo4j 7687; do sleep 1; done; $*"
else
    docker-compose -f docker/docker-compose-tests.yml run --rm tests
fi
RESULT=$?
docker-compose -f docker/docker-compose-tests.yml rm --stop --force -v
exit ${RESULT}
