// ============================================================
// 02_seed_data.js
// Remplissage avec des données d'exemple
// Usage : mongosh "mongodb://localhost:27017/smartpub_db" 02_seed_data.js
// (à exécuter après 01_setup_collections.js)
// ============================================================

db = db.getSiblingDB("smartpub_db");

// ------------------------------------------------------------
// BADGES (parc limité, réutilisable, indépendant des clients)
// ------------------------------------------------------------
const badges = [
  { badgeUid: "1800723C5701", comment: "Badge Jaune", statut: "disponible" },
  { badgeUid: "3500EB273EC7", comment: "Badge Bleu", statut: "disponible" },
  { badgeUid: "0200AC091FB8", comment: "Badge Rouge", statut: "disponible" },
  { badgeUid: "27004228D09D", comment: "Carte RFID", statut: "hors_service" }
];
db.badges.insertMany(badges);

// ------------------------------------------------------------
// CLIENTS (identité, jamais liée à un badge en dur)
// ------------------------------------------------------------
const clients = [
  {
    nom: "Dupont", prenom: "Julien",
    email: "julien.dupont@example.com", telephone: "0032470012345",
    solde: NumberDecimal("25.00"), dateCreation: new Date(),
    actif: true, banni: false
  },
  {
    nom: "Martin", prenom: "Léa",
    email: "lea.martin@example.com", telephone: "0032470098765",
    solde: NumberDecimal("10.50"), dateCreation: new Date(),
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
const catBoissonId = db.categories_produits.insertOne({ nom: "Boisson", poste: "bar" }).insertedId;
const catSnackId = db.categories_produits.insertOne({ nom: "Snack", poste: "cuisine" }).insertedId;
const catPlatId = db.categories_produits.insertOne({ nom: "Plat", poste: "cuisine" }).insertedId;

db.produits.insertMany([
  { nom: "Coca", categorieId: catBoissonId, prix: NumberDecimal("2.50"), tauxTVA: NumberDecimal("0.21"), stock: 120, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { nom: "Fanta", categorieId: catBoissonId, prix: NumberDecimal("2.50"), tauxTVA: NumberDecimal("0.21"), stock: 100, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { nom: "Sprite", categorieId: catBoissonId, prix: NumberDecimal("2.50"), tauxTVA: NumberDecimal("0.21"), stock: 100, seuilAlerteStock: 20, unite: "canette", disponible: true },
  { nom: "Biere", categorieId: catBoissonId, prix: NumberDecimal("3.00"), tauxTVA: NumberDecimal("0.21"), stock: 200, seuilAlerteStock: 40, unite: "bouteille", disponible: true },
  { nom: "Chips", categorieId: catSnackId, prix: NumberDecimal("2.00"), tauxTVA: NumberDecimal("0.06"), stock: 50, seuilAlerteStock: 10, unite: "sachet", disponible: true },
  { nom: "Saucisson", categorieId: catSnackId, prix: NumberDecimal("4.50"), tauxTVA: NumberDecimal("0.06"), stock: 30, seuilAlerteStock: 5, unite: "planche", disponible: true },
  { nom: "Pizza", categorieId: catPlatId, prix: NumberDecimal("8.00"), tauxTVA: NumberDecimal("0.06"), stock: 25, seuilAlerteStock: 5, unite: "piece", disponible: true }
]);

// ------------------------------------------------------------
// EMPLOYES
// ------------------------------------------------------------
db.employes.insertMany([
  { nom: "Sophie B.", role: "barman", pin: "1234", actif: true },
  { nom: "Marc L.", role: "cuisinier", pin: "5678", actif: true },
  { nom: "Alex R.", role: "gerant", pin: "0000", actif: true }
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

const visiteId = db.visites.insertOne({
  badgeId: badgeAttribue._id,
  clientId: clientDupont._id,
  tableNumero: 1,
  dateArrivee: new Date(),
  dateDepart: null,
  statut: "ouverte",
  montantTotalVisite: NumberDecimal("0.00"),
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

const montantTotal = lignes.reduce(
  (acc, l) => acc + (l.prixUnitaireSnapshot * l.quantite),
  NumberDecimal("0.00")
);

db.commandes.insertOne({
  visiteId: visiteActive._id, // <-- seul lien conservé, jamais badgeId/clientId en direct
  employeId: null,
  dateCommande: new Date(),
  statut: "en_attente",
  montantTotal: montantTotal,
  source: "rpi",
  lignes: lignes
});

print(">> Données de seed insérées avec succès.");
print(">> Badge attribué : " + badgeAttribue.badgeUid);
print(">> Visite créée   : " + visiteId);
