
I'll use send grid to send an email after each visit, containing the photos taken during visit.

# 1. setup
signup.sendgrid.com

# 2. dashboard 
https://app.sendgrid.com/guide

# 3. Install sendgrid in container
```bash
docker exec -it node-red-employee bash
cd /data
npm install @sendgrid/mail
```

# 4. Setup single sender 
https://app.sendgrid.com/settings/sender_auth/senders

# 5. Test sendgrid 
```bash
curl --request POST \
  --url https://api.sendgrid.com/v3/mail/send \
  --header "Authorization: Bearer SG." \
  --header "Content-Type: application/json" \
  --data '{
    "personalizations": [{"to": [{"email": "clement.lemlijn@student.hepl.be"}]}],
    "from": {"email": "clement.lemlijn@student.hepl.be"},
    "subject": "Test isolation SendGrid",
    "content": [{"type": "text/plain", "value": "Ceci est un test direct API."}]
  }'
```
