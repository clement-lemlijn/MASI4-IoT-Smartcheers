# Cisco webex 


step 1 : bot creation :
https://developer.webex.com/my-apps/new

step 2 : space creation : 
https://web.webex.com/spaces/create-space

step 3 : test bot 
curl -X GET https://webexapis.com/v1/rooms \
  -H "Authorization: Bearer BOT_TOKEN"

step 4 : send msg 
curl -X POST https://webexapis.com/v1/messages \
  -H "Authorization: Bearer BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roomId": "ROOM_ID",
    "markdown": "🔴 **TEST** — Bot Smartcheers connecté avec succès"
  }'
