from umqtt.simple import MQTTClient
client=MQTTClient("XYX17","192.168.0.10")#client ID, followed by broker addr
client.connect()
client.publish("esys/XYX17",bytes("message",'utf-8'))

