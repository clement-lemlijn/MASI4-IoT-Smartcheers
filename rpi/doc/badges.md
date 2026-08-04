


|Badge|ID|
| :--- | :--- |
|Badge Jaune|1800723C5701|
|Badge Bleu|3500EB273EC7|
|Badge Rouge|0200AC091FB8|
|Carte RFID|27004228D09D|


```js
use("SmartCheers_Database");

db.badges.insertMany([
    {
        name: "Badge Jaune",
        id: "1800723C5701"
    },
    {
        name: "Badge Bleu",
        id: "3500EB273EC7"
    },
    {
        name: "Badge Rouge",
        id: "0200AC091FB8"
    },
    {
        name: "Carte RFID",
        id: "27004228D09D"
    }
]);

print("Collection 'badges' initialisée avec succès.");
```
