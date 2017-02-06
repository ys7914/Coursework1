import network
ap_if=network.WLAN(network.AP_IF)
ap_if.active(False)#turn off automatic receiving
sta_if.active(True)#turn on transmitting
sta_if=network.WLAN(network.STA_IF)
sta_if.connect('EEERover','exhibition')#connect to internet
sta_if.isconnected()
