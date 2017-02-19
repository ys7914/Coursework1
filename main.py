from machine import Pin, I2C
import utime
print('XYX17 presents the Habitus Coach!')
############Connecting To Network#####################################
import network
ap_if=network.WLAN(network.AP_IF)
ap_if.active(False)#turn off automatic receiving
sta_if=network.WLAN(network.STA_IF)
sta_if.active(True)#turn on transmitting
sta_if.connect('EEERover','exhibition')#connect to internet
while not sta_if.isconnected():
    utime.sleep(0.1)#checking connection to internet before connecting to MQTT broker
print('Connected to EEERover')

###################Connecting To Broker and Setting Clock on Device########################
from umqtt.simple import MQTTClient
client=MQTTClient("XYX17","192.168.0.10")#client ID, followed by broker addr
client.connect()

import ujson as json

def sub_cb(topic, msg):
    global time0
    print((topic,msg))
    timetemp=json.loads(msg)
    time0=timetemp['date']
    print('Time from the broker is: ', time0)
    
client.set_callback(sub_cb)
client.subscribe('esys/time')
print('Waiting for server time...')
client.wait_msg()

import machine
rtc=machine.RTC()
rtc.datetime((int(time0[0:4]),int(time0[5:7]),int(time0[8:10]),0,int(time0[11:13]),int(time0[14:16]),int(time0[17:19]),int(time0[20:22])))
print('Device time:', rtc.datetime())

##############Reading and Processing of Sensor Data###################################
def getvalues(reg_addr):
    data_l=i2c.readfrom_mem(24,reg_addr,1)
    data_h=i2c.readfrom_mem(24,reg_addr+1,1)
    value=(int(data_h[0])<<2)+(int(data_l[0])>>6)#10 Bit accuracy 
    if(0x80 & data_h[0]==0x80):
        value-=1024#converting to negative no from 2's complement
    value=value/256*9.81#converting to m/s^2 unit
    return value

i2c=I2C(scl=Pin(5),sda=Pin(4),freq=100000)#setting up i2c comms
i2c.writeto_mem(24,0x20,b'\x57')#setting the device to normal mode
ledr=machine.Pin(13,machine.Pin.OUT)
ledg=machine.Pin(15,machine.Pin.OUT)

cycleT=1.0
direction="IDLE" #default
count=0 #counts cycles "AWAKE"
countni=0 #counts cycles not "IDLE"
listData=[] #list of tuple (direction, utime.localtime()) that can be used to plot graph (future extension)
state=True

while state:
    datax=getvalues(0x28)#reading of x axis acceleration  
    datay=getvalues(0x2A)#reading of y axis acceleration
    dataz=getvalues(0x2C)#reading of z axis acceleration

    #checking of orientation
    #when "Awake", both LEDs light up
    if datax<-8:
        direction="Awake"
        ledg.high()
        ledr.high()
        count=count+1
        countni=countni+1
    #when "Side Sleeping (Right)", green LED (right side) lights up
    elif datay>7:
        direction="Side Sleeping (Right)"
        ledg.high()
        ledr.low()
        count=0
        countni=countni+1
    #when "Side Sleeping (Left)", red LED (left side) lights up
    elif datay<-7:
        direction="Side Sleeping (Left)"
        ledg.low()
        ledr.high()
        count=0
        countni=countni+1
    #when "Back Sleeping", both LEDs are off
    elif dataz>7:
        direction="Back Sleeping"
        ledg.low()
        ledr.low()
        count=0
        countni=countni+1
    #when "Stomach Sleeping", LEDs blink (warning for bad posture)
    elif dataz<-7:
        direction="Stomach Sleeping"
        ledg.high()
        ledr.high()
        utime.sleep(cycleT/2.0)
        ledg.low()
        ledr.low()
        utime.sleep(cycleT/2.0)
        count=0
        countni=countni+1
    #"IDLE" when device is oriented upside down (unlikely to happen when user is sleeping), both LEDs are off
    else:
        direction="IDLE"
        ledg.low()
        ledr.low()
        count=0
        countni=0

    #keeping the delay constant
    if dataz>-7: #if not "Stomach Sleeping"
        utime.sleep(cycleT)

    print('raw x: ',"%.2f"%datax)
    print('raw y: ',"%.2f"%datay)
    print('raw z: ',"%.2f"%dataz)
    print(direction)
    print(utime.localtime())
    print()
        
    if countni>=10: #only send data to server if not "IDLE" for 10 cycles or more
        listData.append((direction,utime.localtime()))
        
        payload=json.dumps({"x axis": "%.2f"%datax, "y axis": "%.2f"%datay, "z axis": "%.2f"%dataz, "direction": direction, "time":utime.localtime()})

        #publishing to the broker
        client.publish("esys/XYX17",bytes(payload,'utf-8'))

        if count==10: #if "AWAKE" for 10 cycles (for actual product this condition might be changed to count==600 [~10min])
            print(listData)
            payload=json.dumps({"Data": listData})
            client.publish("esys/XYX17",bytes(payload,'utf-8'))
            ledg.low()
            ledr.low()
            state=False
      
