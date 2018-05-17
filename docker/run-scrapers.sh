#!/bin/bash

if [ -n "${CA_URL}" ] && [ ! -f "/tmp/.imported" ]; then
    # Since update-ca-trust doesn't work as a non-root user, let's just append to the bundle directly
    curl --silent --show-error "${CA_URL}" >> /etc/pki/tls/certs/ca-bundle.crt
    # Create a file so we know not to import it again if the container is restarted
    touch /tmp/.imported
fi

exec python3 scripts/scrape.py $SCRAPER \
    --teiid-user $TEIID_USER \
    --teiid-password $TEIID_PASSWORD \
    --neo4j-user $NEO4J_USER \
    --neo4j-password $NEO4J_PASSWORD \
    --neo4j-server $NEO4J_SERVER \
    --days-ago $SCRAPE_FROM_DAYS_AGO
