sudo chown -R lemlijn-clement:lemlijn-clement ../config/certs


lemlijn-clement@VM-Orion:~/copy-certs$ sudo cp -r ~/MASI4-IoT-Smartcheers/vm2-orion/mqtt-broker/config/certs ~/copy-certs/
lemlijn-clement@VM-Orion:~/copy-certs$ sudo chown -R lemlijn-clement:lemlijn-clement certs


chmod +x generate-certs.sh
./generate-certs.sh


chmod +x generate-node-red-certs.sh
sudo ./generate-node-red-certs.sh
