# First api run : 

```
sudo docker build -t mon-api-odata .
sudo docker run -d -p 5000:5000 --name api-odata --network host mon-api-odata
```
