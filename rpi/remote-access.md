
# Pour pouvoir accéder au Rpi en "remote development"

- **IntelliJ IDEA Ultimate** : `File` -> `Remote Development`
- **VSCode** : `Extensions` -> `Remote - SSH` (by Microsoft)

Ne fonctionnent pas car Rpi tourne sous **Raspbian 10 (Buster)** en **ARMv7(32bits)**.

Une solution quick & dirty est donc de monter le dossier du Pi avec [WinFsp](https://winfsp.dev/) ainsi que [SSHFS-Win](https://github.com/winfsp/sshfs-win).

<p align="center">
  <img src="https://winfsp.dev/logo.png" alt="WinFsp Logo" width="400">
  <img src="https://github.com/winfsp/sshfs-win/raw/master/art/sshfs-glow.png" alt="SSHFS-Win Logo" width="400">
</p>

<img src="../assets/MASI4-IoT-Smartcheers-Remote_Mount_Rpi.png" alt="Remote config RPI" width="800">
