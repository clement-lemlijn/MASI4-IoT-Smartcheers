
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
