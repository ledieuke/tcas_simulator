from adsbReceiver import AdsbReceiver
from adsbEmitter import AdsbEmitter

class Adsb:
    def __init__(self, aircraftIntruders):
        #Same dictionary that the aircraft has
        self.aircraftIntruders = aircraftIntruders

        #Attach a ADS-B Receiver and ADS-B Emitter
        self.adsbReceiver = AdsbReceiver(self.aircraftIntruders)
        self.adsbEmitter = AdsbEmitter()