#!/usr/bin/env bash
# This script runs the test suite using Docker and Docker Compose

for dir in purview tests; do
    find ${dir} -type f \( -name '*.pyc' -or -name '*.pyc' \) -exec rm -f {} \;
done

docker-compose -f docker-compose-tests.yml up -d neo4j
docker-compose -f docker-compose-tests.yml run --rm tests
RESULT=$?
docker-compose -f docker-compose-tests.yml rm --stop --force -v
exit ${RESULT}
