# First api run : 

```
sudo docker build -t mon-api-odata .
sudo docker run -d -p 5000:5000 --name api-odata --network host mon-api-odata
```

## Test API. 
```
sudo docker exec -it api-odata python -c "from pymongo import MongoClient; c=MongoClient('mongodb://nodered:pwd-to-mongo19@mongodb:27017/?authSource=smartpub_db'); print(c.admin.command('ping')); print(c['smartpub_db']['sensors'].find_one())"
```

## Requests : 

### Température supérieure à 22 °C
```
curl -u admin:motdepassefort123 \
  'http://192.168.1.12:5000/odata/Mesures?$top=1'
```

### Limiter à 1 résultat
```
curl -u admin:motdepassefort123 \
  'http://192.168.1.12:5000/odata/Mesures?$top=1'
```

### Température inférieure ou égale à 21.5
```
curl -u admin:motdepassefort123 \
  'http://192.168.1.12:5000/odata/Mesures?$filter=temperature%20le%2021.5'
```
