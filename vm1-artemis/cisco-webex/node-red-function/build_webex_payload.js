// msg.payload attendu: { bar_id, event_type, details }
const barId = msg.payload.bar_id;
const eventType = msg.payload.event_type; // "device_offline", "db_error", "report"
const details = msg.payload.details;

// Anti-spam: 1 alerte du même type par bar toutes les 15min max
const key = `webex_last_${barId}_${eventType}`;
const lastSent = flow.get(key) || 0;
const now = Date.now();
const COOLDOWN_MS = 15 * 60 * 1000;

if (now - lastSent < COOLDOWN_MS) {
    node.status({fill:"yellow", shape:"dot", text:"anti-spam: skipped"});
    return null; // on ne propage rien
}

flow.set(key, now);

// Récupérer le roomId du bar (via un lookup préalable ou global context)
const rooms = global.get("bar_webex_rooms") || {};
const roomId = rooms[barId];

if (!roomId) {
    node.warn(`Pas de roomId Webex pour bar ${barId}`);
    return null;
}

const icons = {
    device_offline: "🔴",
    db_error: "⚠️",
    report: "📊",
    security: "🔒"
};

msg.payload = {
    roomId: roomId,
    markdown: `${icons[eventType] || "ℹ️"} **${eventType.toUpperCase()}** — ${new Date().toISOString()}\n\n${details}`
};
node.status({fill:"green", shape:"dot", text:`sent: ${eventType}`});
return msg;