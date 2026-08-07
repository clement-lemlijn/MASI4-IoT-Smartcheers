// ============================================================
// 02_seed_data.js
// Remplissage avec des données d'exemple
// Usage : mongosh "mongodb://localhost:27017/smartpub_db" 02_seed_data.js
// (à exécuter après 01_setup_collections.js)
// ============================================================

db = db.getSiblingDB("smartpub_db");

const { randomUUID } = require("crypto");

// ------------------------------------------------------------
// RPIS
// Parc des Raspberry Pi utilisés comme bornes de commande
// ------------------------------------------------------------

const raspberrypis = [
  {
    _id: randomUUID(),
    rpiId: "rpi-002",
    nom: "Borne Table 2",
    emplacement: "Table 2",
    statut: "actif",
    derniereConnexion: null
  },
];

db.raspberrypi.insertMany(raspberrypis);

const rpi2 = db.raspberrypi.findOne({ rpiId: "rpi-002" });
const rpi2Id = rpi2._id;

// ------------------------------------------------------------
// SENSORS
// Capteurs ESP32-H2 de démonstration
// ------------------------------------------------------------

const sensors = [
  {
    _id: randomUUID(),
    deviceId: "esp32h2-102",
    temperature: 22.0,
    humidity: 50.0,
    sound: 705,
    timestamp: new Date()
  },
  {
    _id: randomUUID(),
    deviceId: "esp32h2-103",
    temperature: 21.5,
    humidity: 54.0,
    sound: 420,
    timestamp: new Date()
  }
];

db.sensors.insertMany(sensors);

// ------------------------------------------------------------
// BADGES (parc limité, réutilisable, indépendant des clients)
// ------------------------------------------------------------
const badges = [
  { _id: randomUUID(), badgeUid: "1800723C5701", comment: "Badge Jaunee", statut: "disponible" },
  { _id: randomUUID(), badgeUid: "3500EB273EC7", comment: "Badge Bleu", statut: "disponible" },
  { _id: randomUUID(), badgeUid: "0200AC091FB8", comment: "Badge Rouge", statut: "hors_service" },
  { _id: randomUUID(), badgeUid: "27004228D09D", comment: "Carte RFID", statut: "disponible" }
];
db.badges.insertMany(badges);

// ------------------------------------------------------------
// CLIENTS (identité, jamais liée à un badge en dur)
// ------------------------------------------------------------
const clients = [
  {
    _id: randomUUID(),
    nom: "Dupont", prenom: "Julien",
    email: "julien.dupont@example.com", telephone: "0032470012345",
    solde: 25.00, dateCreation: new Date(),
    actif: true, banni: false
  },
  {
    _id: randomUUID(),
    nom: "Martin", prenom: "Léa",
    email: "lea.martin@example.com", telephone: "0032470098765",
    solde: 10.50, dateCreation: new Date(),
    actif: true, banni: false
  }
];
db.clients.insertMany(clients);
const clientDupont = db.clients.findOne({ nom: "Dupont" });

// ------------------------------------------------------------
// TABLES
// ------------------------------------------------------------
db.tables.insertMany([
  { numero: 1, capacite: 4, zone: "salle", statut: "libre" },
  { numero: 2, capacite: 6, rpiId: rpi2Id, zone: "terrasse", statut: "libre" },
  { numero: 3, capacite: 2, zone: "bar", statut: "libre" },
  { numero: 4, capacite: 8, zone: "vip", statut: "libre" }
]);

// ------------------------------------------------------------
// CATEGORIES + PRODUITS
// ------------------------------------------------------------
const catBoissonId = randomUUID();
    db.categories_produits.insertOne({ _id: catBoissonId, nom: "Boisson", poste: "bar" });
const catSnackId = randomUUID();
    db.categories_produits.insertOne({ _id: catSnackId, nom: "Snack", poste: "cuisine" });
const catPlatId = randomUUID();
    db.categories_produits.insertOne({ _id: catPlatId, nom: "Plat", poste: "cuisine" });

db.produits.insertMany([
  { _id: randomUUID(), nom: "Coca", categorieId: catBoissonId, produitId: "a2138356-7baf-4142-b468-02b7fbca4253", prix: 2.50, tauxTVA: 0.21, stock: 120, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { _id: randomUUID(), nom: "Fanta", categorieId: catBoissonId, produitId: "9e16479d-5211-4270-912b-9b590c8180df", prix: 2.50, tauxTVA: 0.21, stock: 100, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { _id: randomUUID(), nom: "Sprite", categorieId: catBoissonId, produitId: "11a8568f-966b-4466-a51b-198edc020a68", prix: 2.50, tauxTVA: 0.21, stock: 100, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { _id: randomUUID(), nom: "Biere", categorieId: catBoissonId, produitId: "d0b5af66-994e-40b9-8ca7-7904b9c395b4", prix: 3.00, tauxTVA: 0.21, stock: 200, seuilAlerteStock: 40, unite: "bouteille", disponible: true },
  { _id: randomUUID(), nom: "Chips", categorieId: catSnackId, produitId: "e24a1365-c421-46a3-960f-462a14580008", prix: 2.00, tauxTVA: 0.06, stock: 50, seuilAlerteStock: 10, unite: "sachet", disponible: true },
  { _id: randomUUID(), nom: "Saucisson", categorieId: catSnackId, produitId: "dfde3f18-9679-44d6-9335-c283fb92bd95", prix: 4.50, tauxTVA: 0.06, stock: 30, seuilAlerteStock: 5, unite: "planche", disponible: true },
  { _id: randomUUID(), nom: "Pizza", categorieId: catPlatId, produitId: "35ba79f7-e6a9-4dbf-9e28-0492b249b44e", prix: 8.00, tauxTVA: 0.06, stock: 25, seuilAlerteStock: 5, unite: "piece", disponible: true }
]);

// ------------------------------------------------------------
// EMPLOYES
// ------------------------------------------------------------
db.employes.insertMany([
  { _id: randomUUID(), nom: "Sophie B.", role: "barman", pin: "1234", actif: true },
  { _id: randomUUID(), nom: "Marc L.", role: "cuisinier", pin: "5678", actif: true },
  { _id: randomUUID(), nom: "Alex R.", role: "gerant", pin: "0000", actif: true }
]);

// ------------------------------------------------------------
// ATTRIBUTION D'UN BADGE => création de la VISITE
// (ce bloc représente ce qui se passe à l'entrée du client :
//  on lui prête un badge disponible pour la durée de sa présence)
// ------------------------------------------------------------
const badgeAttribue = db.badges.findOne({
  badgeUid: "27004228D09D",
  statut: "disponible"
});
if (!badgeAttribue) {
  throw new Error("Badge indisponible pour l'attribution.");
}

db.badges.updateOne({ _id: badgeAttribue._id }, { $set: { statut: "attribue" } });

const visiteId = randomUUID();

db.visites.insertOne({
  _id: visiteId,
  badgeId: badgeAttribue._id,
  clientId: clientDupont._id,
  token: "d3775d49",   // <-------------------------------------------------- static token for now 
  tableNumero: 2,
  dateArrivee: new Date(),
  dateDepart: null,
  statut: "ouverte",
  montantTotalVisite: 0.00,
  paiement: null
}).insertedId;

db.tables.updateOne({ numero: 2 }, { $set: { statut: "occupee" } });

// ------------------------------------------------------------
// COMMANDE d'exemple : le RPI envoie le badgeUid scanné,
// PAS un identifiant de client. On retrouve la visite ouverte
// correspondante pour savoir qui commande et où.
// ------------------------------------------------------------
function getProduit(nom) {
  return db.produits.findOne({ nom: nom });
}

const payloadRPI = {
  badgeUid: "27004228D09D", // <-- champ physiquement scanné par le RPI
  command: [
    { produit: "Coca", quantite: 1 },
    { produit: "Fanta", quantite: 1 },
    { produit: "Sprite", quantite: 1 },
    { produit: "Biere", quantite: 1 },
    { produit: "Chips", quantite: 1 },
    { produit: "Saucisson", quantite: 1 },
    { produit: "Pizza", quantite: 1 }
  ]
};

const badgeScanne = db.badges.findOne({ badgeUid: payloadRPI.badgeUid });
const visiteActive = db.visites.findOne({ badgeId: badgeScanne._id, statut: "ouverte" });
if (!visiteActive) {
  throw new Error("Aucune visite ouverte pour ce badge : commande refusée.");
}

const lignes = payloadRPI.command.map(item => {
  const p = getProduit(item.produit);
  return {
    produitId: p._id,
    produitNomSnapshot: p.nom,
    quantite: item.quantite,
    prixUnitaireSnapshot: p.prix,
    statutPreparation: "attente",
    poste: db.categories_produits.findOne({ _id: p.categorieId }).poste
  };
});

const montant = lignes.reduce(
  (acc, l) => acc + Number(l.prixUnitaireSnapshot.toString()) * l.quantite,
  0
);

const montantTotal = montant;

db.commandes.insertOne({
  visiteId: visiteActive._id, // <-- seul lien conservé, jamais badgeId/clientId en direct
  employeId: null,
  dateCommande: new Date(),
  statut: "en_attente",
  montantTotal: montantTotal,
  source: "rpi",
  lignes: lignes
});

// ------------------------------------------------------------
// MENU (affichage client, avec image)
// Les URLs d'images sont des placeholders de demo (placehold.co) :
// remplace-les par tes vraies photos une fois disponibles.
// ------------------------------------------------------------
db.menu.insertMany([
  {
    nom: "Coca-Cola 33cl",
    description: "Boisson gazeuse au cola servie fraîche",
    categorie: "Boisson",
    prix: 2.50,
    imageUrl: "https://lh3.googleusercontent.com/d/1vdeihY291c5xhvx9CSPRs6SeKSjMuyMP",
    disponible: true
  },
  {
    nom: "Fanta Orange 33cl",
    description: "Boisson gazeuse à l'orange servie fraîche",
    categorie: "Boisson",
    prix: 2.50,
    imageUrl: "https://lh3.googleusercontent.com/d/1ON49dkxScge6-0XxqL154JctPJ2_GjSe",
    disponible: true
  },
  {
    nom: "Sprite 33cl",
    description: "Boisson gazeuse citron-lime servie fraîche",
    categorie: "Boisson",
    prix: 2.50,
    imageUrl: "https://lh3.googleusercontent.com/d/1qkFIt6BS4PJYmsxWSKzuwrUzrf6WwaQQ",
    disponible: true
  },
  {
    nom: "Bière Jupiler 33cl",
    description: "Bière belge blonde, 5.2%",
    categorie: "Boisson",
    prix: 4.50,
    imageUrl: "https://lh3.googleusercontent.com/d/1lG8y59m4zbRgt_BwUrb2uxuF2XeWTeI4",
    disponible: true
  },
  {
    nom: "Chips",
    description: "Plat de chips croustillantes",
    categorie: "Snack",
    prix: 2.00,
    imageUrl: "https://lh3.googleusercontent.com/d/1e1Ia_qanuedHiv3l-TFFm4s01hmAou2l",
    disponible: true
  },
  {
    nom: "Saucisson",
    description: "Tranches de saucisson sec à partager",
    categorie: "Snack",
    prix: 3.50,
    imageUrl: "https://lh3.googleusercontent.com/d/14tCIo8wBNjbI3J5dRAnGqQ8YecNLOCX7",
    disponible: true
  },
  {
    nom: "Pizza apéritive",
    description: "Morceaux de pizza à partager pour l'apéritif",
    categorie: "Snack",
    prix: 5.00,
    imageUrl: "https://lh3.googleusercontent.com/d/1l8iGiruKAy4QV1vwE2iEK3QbRJlhjYyo",
    disponible: true
  }
]);


print(">> Données de seed insérées avec succès.");
print(">> Badge attribué : " + badgeAttribue.badgeUid);
print(">> Visite créée   : " + visiteId);
