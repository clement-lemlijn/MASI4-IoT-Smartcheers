sudo chown -R lemlijn-clement:lemlijn-clement ../config/certs

chmod +x generate-certs.sh
./generate-certs.sh


chmod +x generate-node-red-certs.sh
sudo ./generate-node-red-certs.sh
