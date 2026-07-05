#!/bin/bash

CERT_DIR="../config/certs"
mkdir -p $CERT_DIR

echo "--- Génération des certificats SmartCheers ---"

# 1. Génération de l'Autorité de Certification (CA)
openssl genrsa -out $CERT_DIR/ca.key 2048
openssl req -x509 -new -nodes -key $CERT_DIR/ca.key -sha256 -days 365 -out $CERT_DIR/ca.crt \
    -subj "/CN=SmartCheers-CA"

# 2. Génération du certificat SERVEUR
openssl genrsa -out $CERT_DIR/server.key 2048
openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr \
    -subj "/CN=orion-vm"
# Signature par la CA
openssl x509 -req -in $CERT_DIR/server.csr -CA $CERT_DIR/ca.crt -CAkey $CERT_DIR/ca.key \
    -CAcreateserial -out $CERT_DIR/server.crt -days 365 -sha256

# 3. Génération du certificat CLIENT
openssl genrsa -out $CERT_DIR/client.key 2048
openssl req -new -key $CERT_DIR/client.key -out $CERT_DIR/client.csr \
    -subj "/CN=SmartCheers-Client"
# Signature par la CA
openssl x509 -req -in $CERT_DIR/client.csr -CA $CERT_DIR/ca.crt -CAkey $CERT_DIR/ca.key \
    -CAcreateserial -out $CERT_DIR/client.crt -days 365 -sha256

# Nettoyage des fichiers temporaires (CSR)
rm $CERT_DIR/*.csr

echo "--- Certificats générés dans $CERT_DIR ---"
echo "CA, Serveur et Client sont prêts pour le port 8884."
