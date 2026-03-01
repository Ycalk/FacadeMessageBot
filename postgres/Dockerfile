FROM postgres:16-alpine

RUN mkdir -p /etc/postgresql/certs

COPY --chown=postgres:postgres certs/ca/ca.crt /etc/postgresql/certs/ca.crt
COPY --chown=postgres:postgres certs/postgres/postgres.crt /etc/postgresql/certs/server.crt
COPY --chown=postgres:postgres certs/postgres/postgres.key /etc/postgresql/certs/server.key

RUN chmod 644 /etc/postgresql/certs/ca.crt /etc/postgresql/certs/server.crt \
    && chmod 600 /etc/postgresql/certs/server.key

CMD [
  "postgres",
  "-c", "ssl=on",
  "-c", "ssl_cert_file=/etc/postgresql/certs/server.crt",
  "-c", "ssl_key_file=/etc/postgresql/certs/server.key",
  "-c", "ssl_ca_file=/etc/postgresql/certs/ca.crt"
]
