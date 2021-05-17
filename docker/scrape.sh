#!/bin/bash

args=''
if [ -n "${SCRAPE_SINCE}" ]; then
    args+="--since ${SCRAPE_SINCE} "
fi
if [ -n "${SCRAPE_UNTIL}" ]; then
    args+="--until ${SCRAPE_UNTIL}"
fi
if [ ! -n "${args}" ]; then
    args="--days-ago ${SCRAPE_FROM_DAYS_AGO}"
fi

docker/install-ca.sh && \
    sleep $WAIT_FOR && \
    exec python3 scripts/scrape.py $SCRAPER \
        --teiid-user $TEIID_USER \
        --teiid-password $TEIID_PASSWORD \
        --neo4j-user $NEO4J_USER \
        --neo4j-password $NEO4J_PASSWORD \
        --neo4j-server $NEO4J_SERVER \
        --neo4j-scheme "${NEO4J_SCHEME:-bolt}" \
        $args
