#!/bin/bash

set -e

CERT_DIR="../config/certs/employee"
CA_DIR="../config/certs"

mkdir -p "$CERT_DIR"

echo "--- Génération certificat Node-RED Employee HTTPS ---"

# Clé privée
openssl genrsa \
    -out "$CERT_DIR/node-red-employee.key" \
    2048

# CSR
openssl req \
    -new \
    -key "$CERT_DIR/node-red-employee.key" \
    -out "$CERT_DIR/node-red-employee.csr" \
    -subj "/CN=node-red.smartcheers.local"

# Extensions du certificat
cat > "$CERT_DIR/node-red-employee.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names

[alt_names]
DNS.1=node-red.smartcheers.local
IP.1=192.168.1.12
EOF

# Signature avec la CA
openssl x509 \
    -req \
    -in "$CERT_DIR/node-red-employee.csr" \
    -CA "$CA_DIR/ca.crt" \
    -CAkey "$CA_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERT_DIR/node-red-employee.crt" \
    -days 3650 \
    -sha256 \
    -extfile "$CERT_DIR/node-red-employee.ext"

# Nettoyage
rm -f "$CERT_DIR/node-red-employee.csr"
rm -f "$CERT_DIR/node-red-employee.ext"

echo ""
echo "Certificat Node-RED Employee généré avec succès :"
echo "  Clé : $CERT_DIR/node-red-employee.key"
echo "  Certificat : $CERT_DIR/node-red-employee.crt"
