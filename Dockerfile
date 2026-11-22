FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY Harness/studio/package*.json ./
RUN npm ci
COPY Harness/studio/ ./
RUN npm run build

FROM node:22-bookworm-slim AS inspector
WORKDIR /inspector
COPY scripts/inspector-dependencies/package*.json ./
RUN npm ci --omit=dev

FROM python:3.13-slim-bookworm
ARG PRINTLAB_REVISION
LABEL org.opencontainers.image.revision=$PRINTLAB_REVISION
ENV PYTHONPATH=/app/Harness PRINTLAB_ROOT=/app PRINTLAB_STUDIO_PORT=10818 \
    PYTHONUTF8=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
WORKDIR /app
COPY scripts/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock
COPY Harness/ /opt/printlab/Harness/
COPY --from=frontend /build/dist/ /opt/printlab/Harness/studio/dist/
COPY --from=inspector /usr/local/bin/node /usr/local/bin/node
COPY --from=inspector /inspector/ /opt/printlab/Runtime/third-party/bambu-inspector/
COPY Templates/ Templates/
COPY Context/ Context/
COPY Library/ Library/
COPY config/ config/
COPY scripts/init_workspace.py scripts/
COPY scripts/start-container.sh scripts/
COPY AGENTS.md LICENSE.md NOTICE.txt ./
RUN ln -s /opt/printlab/Harness /app/Harness && \
    ln -s /app/Templates /app/config /app/scripts /opt/printlab/ && \
    mkdir -p /opt/printlab/Runtime/venv/bin && \
    ln -s /usr/local/bin/python /opt/printlab/Runtime/venv/bin/python && \
    cp "$SSL_CERT_FILE" /opt/printlab/system-ca.pem && \
    python scripts/init_workspace.py
EXPOSE 10818
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=5 \
    CMD ["python", "-c", "import json, urllib.request; assert json.load(urllib.request.urlopen('http://127.0.0.1:10818/api/health', timeout=2))['ok'] is True"]
CMD ["sh", "scripts/start-container.sh"]
