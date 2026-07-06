#!/bin/bash

CERT_DIR="../config/certs"
mkdir -p "$CERT_DIR"

echo "--- Génération des certificats SmartCheers ---"

# Nettoyage des anciens certificats
rm -f "$CERT_DIR"/*.key
rm -f "$CERT_DIR"/*.crt
rm -f "$CERT_DIR"/*.csr
rm -f "$CERT_DIR"/*.srl
rm -f "$CERT_DIR"/*.ext

# ==================================================
# 1. Génération de l'Autorité de Certification (CA)
# ==================================================

echo "[1/3] Génération de la CA..."

openssl genrsa -out "$CERT_DIR/ca.key" 2048

openssl req \
    -x509 \
    -new \
    -nodes \
    -key "$CERT_DIR/ca.key" \
    -sha256 \
    -days 3650 \
    -out "$CERT_DIR/ca.crt" \
    -subj "/CN=SmartCheers-CA"


# ==================================================
# 2. Génération du certificat SERVEUR MQTT
# ==================================================

echo "[2/3] Génération du certificat serveur MQTT..."

openssl genrsa \
    -out "$CERT_DIR/server.key" \
    2048

openssl req \
    -new \
    -key "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.csr" \
    -subj "/CN=mqtt.smartcheers.local"


# Extensions TLS (SAN)
cat > "$CERT_DIR/server.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names

[alt_names]
DNS.1=mqtt.smartcheers.local
IP.1=192.168.1.12
EOF


openssl x509 \
    -req \
    -in "$CERT_DIR/server.csr" \
    -CA "$CERT_DIR/ca.crt" \
    -CAkey "$CERT_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERT_DIR/server.crt" \
    -days 3650 \
    -sha256 \
    -extfile "$CERT_DIR/server.ext"


# ==================================================
# 3. Génération du certificat CLIENT
# ==================================================

echo "[3/3] Génération du certificat client..."

openssl genrsa \
    -out "$CERT_DIR/client.key" \
    2048

openssl req \
    -new \
    -key "$CERT_DIR/client.key" \
    -out "$CERT_DIR/client.csr" \
    -subj "/CN=SmartCheers-Client"


cat > "$CERT_DIR/client.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
EOF


openssl x509 \
    -req \
    -in "$CERT_DIR/client.csr" \
    -CA "$CERT_DIR/ca.crt" \
    -CAkey "$CERT_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERT_DIR/client.crt" \
    -days 3650 \
    -sha256 \
    -extfile "$CERT_DIR/client.ext"


# ==================================================
# Nettoyage
# ==================================================

rm -f "$CERT_DIR"/*.csr
rm -f "$CERT_DIR"/*.srl
rm -f "$CERT_DIR"/*.ext


echo ""
echo "--- Certificats générés dans $CERT_DIR ---"
echo ""
echo "CA      : ca.crt"
echo "Serveur : server.crt / server.key"
echo "Client  : client.crt / client.key"
echo ""
echo "SAN serveur :"
echo "  DNS:mqtt.smartcheers.local"
echo "  IP:192.168.1.12"
echo ""
echo "MQTT TLS prêt pour le port 8884."
