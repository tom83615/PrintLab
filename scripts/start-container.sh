#!/bin/sh
set -eu

local_ca=/app/Runtime/container-ca.pem
cat /opt/printlab/system-ca.pem > "$SSL_CERT_FILE"
if [ -s "$local_ca" ]; then
    cat "$local_ca" >> "$SSL_CERT_FILE"
fi

exec python -m uvicorn printlab.api:app --host 0.0.0.0 --port 10818 --no-proxy-headers
