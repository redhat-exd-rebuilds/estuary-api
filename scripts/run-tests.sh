#!/usr/bin/env bash
# This script runs the test suite using Docker and Docker Compose

for dir in estuary tests; do
    find ${dir} -type f \( -name '*.pyc' -or -name '*.pyo' \) -exec rm -f {} \;
done

if [ ! -f /tmp/neo4j-plugins/apoc-3.3.0.2-all.jar ]; then
    mkdir -p /tmp/neo4j-plugins
    curl -L https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.3.0.2/apoc-3.3.0.2-all.jar -o /tmp/neo4j-plugins/apoc-3.3.0.2-all.jar
fi

docker-compose -f docker/docker-compose-tests.yml up -d neo4j
if [ "$1" != "" ]; then
    # The user passed at least one argument, so use those arguments as the run command instead
    # of the default
    docker-compose -f docker/docker-compose-tests.yml run --rm estuary_api_tests sh -c "while ! nc -z -w 2 neo4j 7687; do sleep 1; done; $*"
else
    docker-compose -f docker/docker-compose-tests.yml run --rm estuary_api_tests
fi
RESULT=$?
docker-compose -f docker/docker-compose-tests.yml rm --stop --force -v
exit ${RESULT}
