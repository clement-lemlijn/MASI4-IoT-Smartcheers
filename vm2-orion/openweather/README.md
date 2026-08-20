


https://home.openweathermap.org/api_keys


nginx dashboard

```
sudo cp -r ~/openweather-dashboard /var/www/
sudo chown -R www-data:www-data /var/www/openweather-dashboard

# Créer une config Nginx
sudo tee /etc/nginx/sites-available/weather << EOF
server {
    listen 80;
    server_name _;
    root /var/www/openweather-dashboard;
    index index.html;
    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/weather /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```
