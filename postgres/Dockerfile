FROM postgres:16-alpine

RUN mkdir -p /etc/postgresql/certs

COPY --chown=postgres:postgres certs/ca/ca.crt /etc/postgresql/certs/ca.crt
COPY --chown=postgres:postgres certs/postgres/postgres.crt /etc/postgresql/certs/server.crt
COPY --chown=postgres:postgres certs/postgres/postgres.key /etc/postgresql/certs/server.key

RUN chmod 644 /etc/postgresql/certs/ca.crt /etc/postgresql/certs/server.crt \
    && chmod 600 /etc/postgresql/certs/server.key
