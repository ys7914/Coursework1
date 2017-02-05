from machine import Pin, I2C
i2c=I2C(scl=Pin(5),sda=Pin(4),freq=100000)
data=i2c.readfrom_mem(24,0x28,1)
print(data[0])
