# TLS сертификаты сервисов

Этот каталог содержит внутренний CA и сертификаты для сервисов Docker:

- `ca/ca.crt`, `ca/ca.key`
- `redis/redis.crt`, `redis/redis.key`
- `elasticsearch/elasticsearch.crt`, `elasticsearch/elasticsearch.key`
- `cities/cities.crt`, `cities/cities.key`
- `app/app.crt`, `app/app.key`
- `postgres/postgres.crt`, `postgres/postgres.key`

## Генерация

```bash
cd certs
./generate.sh --force
```

Ключи создаются без passphrase для автозапуска контейнеров.
