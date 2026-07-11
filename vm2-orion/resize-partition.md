# 
Lorsqu'on augmente la taille d'un disque virutel depuis VMWare, il faut également que Ubuntu détecte cet espace supplémentaire. 

## Commandes : 

```
lsblk
which growpart
sudo growpart /dev/sda 2
sudo resize2fs /dev/sda2
lsblk
```

## Exécution entière : 
```
lemlijn-clement@VM-Orion:~$ lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
fd0      2:0    1     4K  0 disk 
loop0    7:0    0  73.9M  1 loop /snap/core22/2045
loop1    7:1    0     4K  1 loop /snap/bare/5
loop2    7:2    0  66.8M  1 loop /snap/core24/1643
loop3    7:3    0    74M  1 loop /snap/core22/2411
loop4    7:4    0 245.1M  1 loop /snap/firefox/6565
loop5    7:5    0  11.1M  1 loop /snap/firmware-updater/167
loop6    7:6    0  18.5M  1 loop /snap/firmware-updater/210
loop7    7:7    0  50.1M  1 loop /snap/snapd/27406
loop8    7:8    0 614.5M  1 loop /snap/gnome-46-2404/164
loop9    7:9    0 531.4M  1 loop /snap/gnome-42-2204/247
loop10   7:10   0   395M  1 loop /snap/mesa-2404/1165
loop11   7:11   0 531.5M  1 loop /snap/gnome-42-2204/263
loop12   7:12   0  48.1M  1 loop /snap/snapd/25935
loop13   7:13   0  15.7M  1 loop /snap/snap-store/1367
loop14   7:14   0 251.6M  1 loop /snap/firefox/7836
loop15   7:15   0   576K  1 loop /snap/snapd-desktop-integration/315
loop16   7:16   0   576K  1 loop /snap/snapd-desktop-integration/343
loop17   7:17   0  91.7M  1 loop /snap/gtk-common-themes/1535
loop18   7:18   0  10.8M  1 loop /snap/snap-store/1270
sda      8:0    0    40G  0 disk 
├─sda1   8:1    0     1M  0 part 
└─sda2   8:2    0    20G  0 part /
sr0     11:0    1  95.3M  0 rom  /media/lemlijn-clement/CDROM
sr1     11:1    1   5.9G  0 rom  /media/lemlijn-clement/Ubuntu 24.04.3 LTS amd64
lemlijn-clement@VM-Orion:~$ which growpart
/usr/bin/growpart
lemlijn-clement@VM-Orion:~$ sudo growpart /dev/sda 2
[sudo] password for lemlijn-clement: 
CHANGED: partition=2 start=4096 old: size=41936896 end=41940991 new: size=83881951 end=83886046
lemlijn-clement@VM-Orion:~$ sudo resize2fs /dev/sda2
resize2fs 1.47.0 (5-Feb-2023)
Filesystem at /dev/sda2 is mounted on /; on-line resizing required
old_desc_blocks = 3, new_desc_blocks = 5
The filesystem on /dev/sda2 is now 10485243 (4k) blocks long.

lemlijn-clement@VM-Orion:~$ lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
fd0      2:0    1     4K  0 disk 
loop0    7:0    0  73.9M  1 loop /snap/core22/2045
loop1    7:1    0     4K  1 loop /snap/bare/5
loop2    7:2    0  66.8M  1 loop /snap/core24/1643
loop3    7:3    0    74M  1 loop /snap/core22/2411
loop4    7:4    0 245.1M  1 loop /snap/firefox/6565
loop5    7:5    0  11.1M  1 loop /snap/firmware-updater/167
loop6    7:6    0  18.5M  1 loop /snap/firmware-updater/210
loop7    7:7    0  50.1M  1 loop /snap/snapd/27406
loop8    7:8    0 614.5M  1 loop /snap/gnome-46-2404/164
loop9    7:9    0 531.4M  1 loop /snap/gnome-42-2204/247
loop10   7:10   0   395M  1 loop /snap/mesa-2404/1165
loop11   7:11   0 531.5M  1 loop /snap/gnome-42-2204/263
loop12   7:12   0  48.1M  1 loop /snap/snapd/25935
loop13   7:13   0  15.7M  1 loop /snap/snap-store/1367
loop14   7:14   0 251.6M  1 loop /snap/firefox/7836
loop15   7:15   0   576K  1 loop /snap/snapd-desktop-integration/315
loop16   7:16   0   576K  1 loop /snap/snapd-desktop-integration/343
loop17   7:17   0  91.7M  1 loop /snap/gtk-common-themes/1535
loop18   7:18   0  10.8M  1 loop /snap/snap-store/1270
sda      8:0    0    40G  0 disk 
├─sda1   8:1    0     1M  0 part 
└─sda2   8:2    0    40G  0 part /
sr0     11:0    1  95.3M  0 rom  /media/lemlijn-clement/CDROM
sr1     11:1    1   5.9G  0 rom  /media/lemlijn-clement/Ubuntu 24.04.3 LTS amd64
lemlijn-clement@VM-Orion:~$ 

```
