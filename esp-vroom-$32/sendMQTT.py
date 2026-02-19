from umqttsimple import *
import time

print("sendMQTT.py")

client = MQTTClient(client_id='testesp', server='192.168.0.222',user='pub',password='pubds8472ds',keepalive=60)
client.connect()

i = 0
while True:
    msg = 'Hello from the ESP side ' + str(i)
    client.publish('test/mqtt', msg)
    print('message sent')
    i+=1
    time.sleep(10)


