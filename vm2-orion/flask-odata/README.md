# First api run : 

```
sudo docker build -t mon-api-odata .
sudo docker run -d -p 5000:5000 --name api-odata --network host mon-api-odata
```

## Test API. 
```
sudo docker exec -it api-odata python -c "from pymongo import MongoClient; c=MongoClient('mongodb://nodered:pwd-to-mongo19@mongodb:27017/?authSource=smartpub_db'); print(c.admin.command('ping')); print(c['smartpub_db']['sensors'].find_one())"
```
