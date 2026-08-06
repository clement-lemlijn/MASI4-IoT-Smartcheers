db = db.getSiblingDB('smartpub_db');

db.createUser({
  user: "nodered",
  pwd: "pwd-to-mongo19",
  roles: [{ role: "readWrite", db: "smartpub_db" }]
});
