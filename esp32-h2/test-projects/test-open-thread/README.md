


## 1. Build les deux projets

Sur chaque ESP32-H2 :
`cd $IDF_PATH/examples/openthread/ot_cli`
`idf.py set-target esp32h2`
`idf.py build`
Flash le premier :
`Bashidf.py -p COMx flash monitor`
Flash le second (dans un autre terminal) :
`Bashidf.py -p COMy flash monitor`

## 2. Former le réseau Thread
### Sur l'ESP32-H2 Leader : 

les commandes suivantes sont censées être préfixées de "ot" (`ot factoryreset`) mais pour une raison inconnue les commandes passent uniquement sans `ot`^

```
factoryreset

dataset init new
dataset commit active
ifconfig up
thread start
state

dataset active -x
```

### Sur l'ESP32-H2 Router : 

```
factoryreset

dataset set active <colle ici le long dataset>
ifconfig up
thread start
state
```
