# 🍻 SmartCheers – VM Orion - Arduino

## Installation d'arduino (1.8.19)

```
sudo apt update
sudo apt install python3-serial
sudo apt install python3-pip
pip install esptool

# télécharger sur arduino.cc/en/software la version linux 64 bits :
 arduino-1.8.19-linux64.tar.xz
# extraire par :
tar -xf arduino-1.8.19-linux64.tar.xz
# dans le répertoire arduino-1.8.19 :
sudo ./install.sh
# supprimer l’archive arduino-1.8.19-linux64.tar.xz
```
## Installation software Heltec-esp32s3-lora (dans arduino)

```
sudo usermod -a -G dialout $USER
sudo apt-get install git
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
mkdir -p ~/Arduino/hardware/heltec
cd ~/Arduino/hardware/heltec
git clone https://github.com/Heltec-Aaron-Lee/WiFi_Kit_series.git esp32
cd esp32
git submodule update --init --recursive
cd tools
python3 get.py
```
