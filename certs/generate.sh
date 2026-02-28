#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_DIR="${BASE_DIR}/ca"
SERVICES=(redis elasticsearch cities app postgres)

mkdir -p "${CA_DIR}"
for svc in "${SERVICES[@]}"; do
  mkdir -p "${BASE_DIR}/${svc}"
done

if [[ "${1:-}" == "--force" ]]; then
  rm -f "${CA_DIR}/ca.crt" "${CA_DIR}/ca.key" "${CA_DIR}/ca.srl"
  for svc in "${SERVICES[@]}"; do
    rm -f "${BASE_DIR}/${svc}/${svc}.crt" "${BASE_DIR}/${svc}/${svc}.key" "${BASE_DIR}/${svc}/${svc}.csr"
  done
fi

if [[ ! -f "${CA_DIR}/ca.crt" || ! -f "${CA_DIR}/ca.key" ]]; then
  ca_ext_file="$(mktemp)"
  cat > "${ca_ext_file}" <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = FacadeMessageBot Internal CA

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, keyCertSign, cRLSign
EOF
  openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
    -keyout "${CA_DIR}/ca.key" \
    -out "${CA_DIR}/ca.crt" \
    -config "${ca_ext_file}" \
    -extensions v3_ca
  rm -f "${ca_ext_file}"
fi

generate_cert() {
  local service="$1"
  shift
  local sans=("$@")

  local service_dir="${BASE_DIR}/${service}"
  local key_file="${service_dir}/${service}.key"
  local csr_file="${service_dir}/${service}.csr"
  local crt_file="${service_dir}/${service}.crt"

  local ext_file
  ext_file="$(mktemp)"
  cat > "${ext_file}" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = ${service}

[v3_req]
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = $(IFS=,; echo "${sans[*]}")
EOF

  openssl req -new -newkey rsa:2048 -nodes \
    -keyout "${key_file}" \
    -out "${csr_file}" \
    -config "${ext_file}"

  openssl x509 -req -sha256 -days 825 \
    -in "${csr_file}" \
    -CA "${CA_DIR}/ca.crt" \
    -CAkey "${CA_DIR}/ca.key" \
    -CAcreateserial \
    -out "${crt_file}" \
    -extfile "${ext_file}" \
    -extensions v3_req

  rm -f "${csr_file}" "${ext_file}"
}

generate_cert "redis" "DNS:redis" "DNS:localhost" "IP:127.0.0.1"
generate_cert "elasticsearch" "DNS:elasticsearch" "DNS:localhost" "IP:127.0.0.1"
generate_cert "cities" "DNS:cities" "DNS:localhost" "IP:127.0.0.1"
generate_cert "app" "DNS:app" "DNS:localhost" "IP:127.0.0.1"
generate_cert "postgres" "DNS:postgres" "DNS:localhost" "IP:127.0.0.1"

chmod 644 "${CA_DIR}/ca.crt"
chmod 600 "${CA_DIR}/ca.key"
for svc in "${SERVICES[@]}"; do
  chmod 644 "${BASE_DIR}/${svc}/${svc}.crt"
  chmod 644 "${BASE_DIR}/${svc}/${svc}.key"
done

echo "Сертификаты успешно сгенерированы в ${BASE_DIR}"
