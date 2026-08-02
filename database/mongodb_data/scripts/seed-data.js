// ============================================================
// 02_seed_data.js
// Remplissage avec des données d'exemple
// Usage : mongosh "mongodb://localhost:27017/smartpub_db" 02_seed_data.js
// (à exécuter après 01_setup_collections.js)
// ============================================================

db = db.getSiblingDB("smartpub_db");

const { randomUUID } = require("crypto");

// ------------------------------------------------------------
// BADGES (parc limité, réutilisable, indépendant des clients)
// ------------------------------------------------------------
const badges = [
  { _id: randomUUID(), badgeUid: "1800723C5701", comment: "Badge Jaunee", statut: "disponible" },
  { _id: randomUUID(), badgeUid: "3500EB273EC7", comment: "Badge Bleu", statut: "disponible" },
  { _id: randomUUID(), badgeUid: "0200AC091FB8", comment: "Badge Rouge", statut: "disponible" },
  { _id: randomUUID(), badgeUid: "27004228D09D", comment: "Carte RFID", statut: "hors_service" }
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
  { numero: 1, capacite: 4, zone: "salle", statut: "occupee" },
  { numero: 2, capacite: 6, zone: "terrasse", statut: "libre" },
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
  { _id: randomUUID(), nom: "Coca", categorieId: catBoissonId, prix: 2.50, tauxTVA: 0.21, stock: 120, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { _id: randomUUID(), nom: "Fanta", categorieId: catBoissonId, prix: 2.50, tauxTVA: 0.21, stock: 100, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { _id: randomUUID(), nom: "Sprite", categorieId: catBoissonId, prix: 2.50, tauxTVA: 0.21, stock: 100, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { _id: randomUUID(), nom: "Biere", categorieId: catBoissonId, prix: 3.00, tauxTVA: 0.21, stock: 200, seuilAlerteStock: 40, unite: "bouteille", disponible: true },
  { _id: randomUUID(), nom: "Chips", categorieId: catSnackId, prix: 2.00, tauxTVA: 0.06, stock: 50, seuilAlerteStock: 10, unite: "sachet", disponible: true },
  { _id: randomUUID(), nom: "Saucisson", categorieId: catSnackId, prix: 4.50, tauxTVA: 0.06, stock: 30, seuilAlerteStock: 5, unite: "planche", disponible: true },
  { _id: randomUUID(), nom: "Pizza", categorieId: catPlatId, prix: 8.00, tauxTVA: 0.06, stock: 25, seuilAlerteStock: 5, unite: "piece", disponible: true }
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
  badgeUid: "1800723C5701",
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
  tableNumero: 1,
  dateArrivee: new Date(),
  dateDepart: null,
  statut: "ouverte",
  montantTotalVisite: 0.00,
  paiement: null
}).insertedId;

// ------------------------------------------------------------
// COMMANDE d'exemple : le RPI envoie le badgeUid scanné,
// PAS un identifiant de client. On retrouve la visite ouverte
// correspondante pour savoir qui commande et où.
// ------------------------------------------------------------
function getProduit(nom) {
  return db.produits.findOne({ nom: nom });
}

const payloadRPI = {
  badgeUid: "1800723C5701", // <-- champ physiquement scanné par le RPI
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
    imageUrl: "https://placehold.co/120x120?text=Coca",
    disponible: true
  },
  {
    nom: "Fanta Orange 33cl",
    description: "Boisson gazeuse à l'orange servie fraîche",
    categorie: "Boisson",
    prix: 2.50,
    imageUrl: "https://placehold.co/120x120?text=Fanta",
    disponible: true
  },
  {
    nom: "Sprite 33cl",
    description: "Boisson gazeuse citron-lime servie fraîche",
    categorie: "Boisson",
    prix: 2.50,
    imageUrl: "https://placehold.co/120x120?text=Sprite",
    disponible: true
  },
  {
    nom: "Bière Jupiler 33cl",
    description: "Bière belge blonde, 5.2%",
    categorie: "Boisson",
    prix: 4.50,
    imageUrl: "https://placehold.co/120x120?text=Jupiler",
    disponible: true
  },
  {
    nom: "Chips",
    description: "Sachet de chips croustillantes",
    categorie: "Snack",
    prix: 2.00,
    imageUrl: "https://placehold.co/120x120?text=Chips",
    disponible: true
  },
  {
    nom: "Saucisson",
    description: "Tranches de saucisson sec à partager",
    categorie: "Snack",
    prix: 3.50,
    imageUrl: "https://placehold.co/120x120?text=Saucisson",
    disponible: true
  },
  {
    nom: "Pizza apéritive",
    description: "Morceaux de pizza à partager pour l'apéritif",
    categorie: "Snack",
    prix: 5.00,
    imageUrl: "https://placehold.co/120x120?text=Pizza",
    disponible: true
  }
]);


print(">> Données de seed insérées avec succès.");
print(">> Badge attribué : " + badgeAttribue.badgeUid);
print(">> Visite créée   : " + visiteId);
