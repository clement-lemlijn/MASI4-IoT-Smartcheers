
# 1. Sécuriser l'éditeur Node-RED adminAuth

(sudo docker exec -it node-red-employee node-red admin hash-pw)

adminAuth: {
    type: "credentials",
    users: [{
        username: "admin",
        password: "$2b$08$S0vPmI1ikOWByDMbQ8k9GewwwDGsQv9uNmmiBrQDcCB1TlwGUn3rO", // <-- votre hash
        permissions: "*"
    }]
},



# 2. Sécuriser les dashboards httpNodeAuth


httpNodeAuth: {
    user: "client",
    pass: "$2y$08$oPfmZftaczdKUATtmcbRQu0odGRRVNyQOa7irY4T9j/XF7jS2Kc.e"
},


# 3. HTTPS pour l'éditeur et les dashboards

