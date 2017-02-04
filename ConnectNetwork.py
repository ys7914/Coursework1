import network
ap_if=network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if.active(True)
sta_if=network.WLAN(network.STA_IF)
sta_if.connect('EEERover','exhibition')
sta_if.isconnected()
