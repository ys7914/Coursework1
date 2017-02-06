from machine import Pin, I2C
import time
i2c=I2C(scl=Pin(5),sda=Pin(4),freq=100000)
##data=i2c.readfrom_mem(24,0x20,1)#check whether in power down mode
##print(data[0]) #7->power down, 87->normal mode
i2c.writeto_mem(24,0x20,b'\x57')

while True:#infinite loop
    data_x_L=i2c.readfrom_mem(24,0x28,1)
    data_x_H=i2c.readfrom_mem(24,0x29,1)
    valuex=(int(data_x_H[0])<<2)+(int(data_x_L[0])>>6)#appending two bytes
    if(0x80 & data_x_H[0]==0x80):
        valuex-=1024#checking sign for two's complement
    print('x axis: ',valuex)
    
    data_y_L=i2c.readfrom_mem(24,0x2A,1)
    data_y_H=i2c.readfrom_mem(24,0x2B,1)
    valuey=(int(data_y_H[0])<<2)+(int(data_y_L[0])>>6)
    if(0x80 & data_y_H[0]==0x80):
        valuey-=1024
    print('y axis: ',valuey)
    
    data_z_L=i2c.readfrom_mem(24,0x2C,1)
    data_z_H=i2c.readfrom_mem(24,0x2D,1)
    valuez=(int(data_z_H[0])<<2)+(int(data_z_L[0])>>6)
    if(0x80 & data_z_H[0]==0x80):
        valuez-=1024
    print('z axis: ',valuez)
    print()
    time.sleep(1.0)
