// init-mongo-artemis.js
// Base dédiée à la télémaintenance multi-clients (Smartcheers)

db = db.getSiblingDB('smartcheers_db');

db.createUser({
  user: "nodered_telemaintenance",
  pwd: "pwd-to-mongo83",
  roles: [{ role: "readWrite", db: "smartcheers_db" }]
});

// Création des collections avec un schéma de base (optionnel mais propre)
db.createCollection("clients");
db.createCollection("telemaintenance_events");
db.createCollection("reports");

// Index utiles
db.clients.createIndex({ nom_bar: 1 }, { unique: true });
db.telemaintenance_events.createIndex({ bar_id: 1, timestamp: -1 });
db.telemaintenance_events.createIndex({ event_type: 1 });
db.reports.createIndex({ bar_id: 1, periode: 1 });
