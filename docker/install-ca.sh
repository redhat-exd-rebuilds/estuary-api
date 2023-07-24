#!/bin/bash

if [ -n "${CA_URLS}" ] && [ ! -f "/tmp/.imported" ]; then
    URLS=($(echo "${CA_URLS}" | tr ',' '\n'))
    # Since update-ca-trust doesn't work as a non-root user, let's just append to the bundle directly
    for url in "${URLS[@]}"; do
        curl -k --silent --show-error "$url" >> /etc/pki/tls/certs/ca-bundle.crt
    done
    # Create a file so we know not to import it again if the container is restarted
    touch /tmp/.imported
fi
