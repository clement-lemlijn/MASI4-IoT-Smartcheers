// ============================================================
// 01_setup_collections.js
// ============================================================

const dbName = "smartpub_db";
db = db.getSiblingDB(dbName);

print(`>> Initialisation de la base ${dbName}`);

// ------------------------------------------------------------
// Nettoyage (optionnel, pratique en dev)
// ------------------------------------------------------------
["pub", "raspberrypi", "badges", "clients", "tables", "categories_produits", "produits", "employes",
 "visites", "commandes", "transactions_credit", "menu",
 "sensors"].forEach(c => {
  db[c].drop();
});

// ------------------------------------------------------------
// PUB
// Informations spécifiques à l'établissement.
// Cette collection ne doit contenir qu'un seul document.
// Pour déployer le système dans un autre bar, il suffit
// de modifier le contenu de ce document.
// ------------------------------------------------------------

db.createCollection("pub", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "nom",
        "nomTechnique",
        "localisation",
        "gerant",
        "contact"
      ],
      properties: {

        nom: {
          bsonType: "string",
          description: "Nom commercial du bar (affiché aux clients)"
        },

        nomTechnique: {
          bsonType: "string",
          description: "Identifiant technique (slug, sans espaces ni accents)"
        },

        localisation: {
          bsonType: "object",
          required: ["adresse", "ville", "codePostal"],
          properties: {
            adresse: {
              bsonType: "string",
              description: "Adresse complète"
            },
            ville: {
              bsonType: "string"
            },
            codePostal: {
              bsonType: "string"
            },
            pays: {
              bsonType: "string",
              description: "Par défaut 'France'"
            },
            coordonnees: {
              bsonType: "object",
              description: "Optionnel – pour cartographie",
              properties: {
                lat: { bsonType: "double" },
                lng: { bsonType: "double" }
              }
            }
          }
        },

        gerant: {
          bsonType: "object",
          required: ["prenom", "nom"],
          properties: {
            prenom: { bsonType: "string" },
            nom:    { bsonType: "string" },
            email:  { bsonType: ["string", "null"] }
          }
        },

        contact: {
          bsonType: "object",
          required: ["telephoneOfficiel"],
          properties: {
            telephoneOfficiel: {
              bsonType: "string",
              description: "Numéro officiel du bar (affiché au public)"
            },
            telephoneGerant: {
              bsonType: ["string", "null"],
              description: "Numéro personnel du gérant"
            },
            email: {
              bsonType: ["string", "null"],
              description: "Email de contact officiel"
            }
          }
        },

        // Champs optionnels utiles
        siret: {
          bsonType: ["string", "null"]
        },

        horaires: {
          bsonType: ["object", "null"],
          description: "Horaires d'ouverture (libre)"
        },

        logoUrl: {
          bsonType: ["string", "null"]
        },

        dateCreation: {
          bsonType: "date"
        },

        actif: {
          bsonType: "bool",
          description: "Permet de désactiver rapidement un établissement"
        }
      }
    }
  }
});
db.pub.createIndex(
    { nomTechnique: 1 },
    { unique: true }
);

// ------------------------------------------------------------
// RPIS
// Terminaux physiques de commande.
// Chaque Raspberry possède un identifiant unique.
// Le RPI communique cet ID avec chaque commande.
// ------------------------------------------------------------

db.createCollection("raspberrypi", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "rpiId",
        "nom",
        "statut"
      ],
      properties: {

        rpiId: {
          bsonType: "string",
          description: "Identifiant unique du Raspberry Pi"
        },

        nom: {
          bsonType: "string",
          description: "Nom lisible du terminal"
        },

        emplacement: {
          bsonType: "string",
          description: "Emplacement physique du RPI"
        },

        statut: {
          enum: [
            "actif",
            "maintenance",
            "hors_service"
          ]
        },

        derniereConnexion: {
          bsonType: [
            "date",
            "null"
          ]
        }
      }
    }
  }
});

db.raspberrypi.createIndex(
  { rpiId: 1 },
  { unique: true }
);

// ------------------------------------------------------------
// SENSORS
// Mesures remontées par les ESP32 Thread
// Chaque document correspond à une mesure instantanée.
// ------------------------------------------------------------

db.createCollection("sensors", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "deviceId",
        "temperature",
        "humidity",
        "sound",
        "timestamp"
      ],

      properties: {

        deviceId: {
          bsonType: "string",
          description: "Identifiant unique du capteur ESP32"
        },

        temperature: {
          bsonType: "number",
          description: "Température en degrés Celsius"
        },

        humidity: {
          bsonType: "number",
          description: "Humidité relative en pourcentage"
        },

        sound: {
          bsonType: "int",
          description: "Niveau sonore mesuré"
        },

        timestamp: {
          bsonType: "date",
          description: "Date de la mesure"
        }
      }
    }
  }
});


// Historique rapide par capteur
db.sensors.createIndex(
  {
    deviceId: 1,
    timestamp: -1
  }
);

// ------------------------------------------------------------
// BADGES
// Ressource physique limitée et réutilisable (tag RFID/NFC).
// Le badgeUid est ce que le RPI lit physiquement. Un badge n'est
// PAS lié à un client de façon permanente : il est prêté le temps
// d'une visite, puis rendu disponible.
// ------------------------------------------------------------
db.createCollection("badges", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["badgeUid", "statut"],
      properties: {
        badgeUid: { bsonType: "string", description: "UID physique du tag, unique" },
        comment: { bsonType: "string", description: "description du badge, hs, etc..." },
        statut: { enum: ["disponible", "attribue", "perdu", "hors_service"] }
      }
    }
  }
});
db.badges.createIndex({ badgeUid: 1 }, { unique: true });

// ------------------------------------------------------------
// CLIENTS
// Identité de la personne, totalement indépendante du badge.
// ------------------------------------------------------------
db.createCollection("clients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["actif", "solde", "dateCreation"],
      properties: {
        nom: { bsonType: "string" },
        prenom: { bsonType: "string" },
        email: { bsonType: ["string", "null"] },
        telephone: { bsonType: ["string", "null"] },
        solde: { bsonType: "number", description: "solde cashless en euros" },
        dateCreation: { bsonType: "date" },
        actif: { bsonType: "bool" },
        banni: { bsonType: "bool" }
      }
    }
  }
});
db.clients.createIndex({ email: 1 }, { unique: true, sparse: true });

// ------------------------------------------------------------
// TABLES
// ------------------------------------------------------------
db.createCollection("tables", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["numero", "capacite", "zone", "statut"],
      properties: {
        numero: { bsonType: "int" },
        capacite: { bsonType: "int" },
        rpiId: { bsonType: "string" }, // ------------------------------------------------------- rpidId => not mandatory
        zone: { enum: ["terrasse", "salle", "bar", "vip"] },
        statut: { enum: ["libre", "occupee", "reservee", "hors_service"] }
      }
    }
  }
});
db.tables.createIndex({ numero: 1 }, { unique: true });

// ------------------------------------------------------------
// CATEGORIES PRODUITS
// ------------------------------------------------------------
db.createCollection("categories_produits", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nom", "poste"],
      properties: {
        nom: { bsonType: "string" },
        poste: { enum: ["bar", "cuisine"] }
      }
    }
  }
});

// ------------------------------------------------------------
// PRODUITS
// ------------------------------------------------------------
db.createCollection("produits", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nom", "categorieId", "produitId", "prix", "disponible", "stock"],
      properties: {
        nom: { bsonType: "string" },
        categorieId: { bsonType: "string" },
        produitId: { bsonType: "string" },
        prix: { bsonType: "number" },
        tauxTVA: { bsonType: "number" },
        stock: { bsonType: "int" },
        seuilAlerteStock: { bsonType: "int" },
        unite: { bsonType: "string" },
        disponible: { bsonType: "bool" }
      }
    }
  }
});
db.produits.createIndex({ nom: 1 }, { unique: true });

// ------------------------------------------------------------
// EMPLOYES
// ------------------------------------------------------------
db.createCollection("employes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nom", "role", "actif"],
      properties: {
        nom: { bsonType: "string" },
        role: { enum: ["serveur", "barman", "cuisinier", "gerant"] },
        pin: { bsonType: "string" },
        actif: { bsonType: "bool" }
      }
    }
  }
});

// ------------------------------------------------------------
// VISITES (assignation client <-> table à un instant T)
// ------------------------------------------------------------
db.createCollection("visites", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["badgeId", "clientId", "token", "tableNumero", "dateArrivee", "statut"],
      properties: {
        badgeId: { bsonType: "string", description: "quel badge physique a été prêté" },
        clientId: { bsonType: "string", description: "quel client a réservé ce badge" },
        token: { bsonType: "string", description: "pour accès à l'interface" },
        tableNumero: { bsonType: "number" },
        dateArrivee: { bsonType: "date" },
        dateDepart: { bsonType: ["date", "null"] },
        statut: { enum: ["ouverte", "fermee", "annulee"] },
        montantTotalVisite: { bsonType: "number" },
        paiement: {
          bsonType: ["object", "null"],
          properties: {
            montant: { bsonType: "number" },
            mode: { enum: ["especes", "carte", "credit_client", null] },
            statut: { enum: ["en_attente", "valide", "refuse", "rembourse", null] },
            datePaiement: { bsonType: ["date", "null"] }
          }
        }
      }
    }
  }
});
db.visites.createIndex({ badgeId: 1, statut: 1 });
db.visites.createIndex({ clientId: 1, statut: 1 });
db.visites.createIndex({ token: 1, statut: 1 });
db.visites.createIndex({ tableNumero: 1, statut: 1 });

// ------------------------------------------------------------
// COMMANDES (lignes embarquées, une commande = un envoi du RPI)
// ------------------------------------------------------------
db.createCollection("commandes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["visiteId", "dateCommande", "statut", "lignes", "montantTotal"],
      properties: {
        visiteId: { bsonType: "string" },
        employeId: { bsonType: ["string", "null"] },
        dateCommande: { bsonType: "date" },
        statut: {
          enum: ["en_attente", "en_preparation", "prete", "envoyee", "servie", "annulee"]
        },
        montantTotal: { bsonType: "number" },
        source: { enum: ["rpi", "caisse", "appli"] },
        lignes: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["produitId", "produitNomSnapshot", "quantite", "prixUnitaireSnapshot"],
            properties: {
              produitId: { bsonType: "string" },
              produitNomSnapshot: { bsonType: "string" },
              quantite: { bsonType: "int", minimum: 1 },
              prixUnitaireSnapshot: { bsonType: "number" },
              statutPreparation: { enum: ["attente", "prepa", "pret", "annule"] },
              poste: { enum: ["bar", "cuisine"] }
            }
          }
        }
      }
    }
  }
});
db.commandes.createIndex({ visiteId: 1 });
db.commandes.createIndex({ statut: 1, dateCommande: 1 });
db.commandes.createIndex({ "lignes.statutPreparation": 1, "lignes.poste": 1 });

// ------------------------------------------------------------
// TRANSACTIONS CREDIT (historique cashless, append-only)
// ------------------------------------------------------------
db.createCollection("transactions_credit", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["clientId", "montant", "type", "date"],
      properties: {
        clientId: { bsonType: "string" },
        montant: { bsonType: "number" },
        type: { enum: ["recharge", "debit", "remboursement"] },
        date: { bsonType: "date" },
        moyenRecharge: { enum: ["cb", "especes", null] }
      }
    }
  }
});
db.transactions_credit.createIndex({ clientId: 1, date: -1 });

// ------------------------------------------------------------
// MENU
// Collection dediee a l'affichage cote client (dashboard Node-RED).
// Distincte de "produits" (qui gere stock/TVA/seuils cote back-office) :
// le menu ne contient QUE ce qui doit etre montre au client (nom, prix,
// description, photo, disponibilite simple).
// ------------------------------------------------------------
db.createCollection("menu", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nom", "categorie", "prix", "disponible"],
      properties: {
        nom: { bsonType: "string" },
        description: { bsonType: ["string", "null"] },
        categorie: { bsonType: "string", description: "ex: Boisson, Snack, Plat" },
        prix: { bsonType: "number" },
        imageUrl: { bsonType: ["string", "null"], description: "URL de la photo de l'item" },
        disponible: { bsonType: "bool" }
      }
    }
  }
});
db.menu.createIndex({ nom: 1 }, { unique: true });


print(">> Collections et index créés avec succès.");
