#!/bin/bash

CERT_DIR="../config/certs"

echo "--- Génération certificat Node-RED HTTPS ---"

openssl genrsa \
    -out "$CERT_DIR/node-red-employee.key" \
    2048


openssl req \
    -new \
    -key "$CERT_DIR/node-red-employee.key" \
    -out "$CERT_DIR/node-red-employee.csr" \
    -subj "/CN=node-red.smartcheers.local"


cat > "$CERT_DIR/node-red.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names

[alt_names]
DNS.1=node-red.smartcheers.local
IP.1=192.168.1.12
EOF


openssl x509 \
    -req \
    -in "$CERT_DIR/node-red-employee.csr" \
    -CA "$CERT_DIR/ca.crt" \
    -CAkey "$CERT_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERT_DIR/node-red-employee.crt" \
    -days 3650 \
    -sha256 \
    -extfile "$CERT_DIR/node-red-employee.ext"


rm "$CERT_DIR/node-red-employee.csr"
rm "$CERT_DIR/node-red-employee.ext"

echo "Certificat Node-RED Employee généré"
