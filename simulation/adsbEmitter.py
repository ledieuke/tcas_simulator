class AdsbEmitter:

    def __init__(self):
        #Dictionary of ADS-B receiver in range
        self.adsbReceiverInRange = {}


    "Emit a ADS-B identification message"
    def emitIdentification(self,aircraft):
        msg = ("Identification", aircraft.icaoAdress, aircraft.callSign)
        for callSign in self.adsbReceiverInRange:
            self.adsbReceiverInRange[callSign].decodeMessage(msg)


    "Emit a ADS-B surface position message"
    def emitSurfacePosition(self,aircraft):
        msg = ("SurfacePosition", aircraft.icaoAdress, aircraft.heading, aircraft.latitude, aircraft.longitude)
        for callSign in self.adsbReceiverInRange:
            self.adsbReceiverInRange[callSign].decodeMessage(msg)


    "Emit a ADS-B airborne position message"
    def emitAirbornePosition(self,aircraft):
        msg = ("AirbornePosition", aircraft.icaoAdress, aircraft.baroaltitude, aircraft.geoaltitude, aircraft.latitude, aircraft.longitude, aircraft.level)
        for callSign in self.adsbReceiverInRange:
            self.adsbReceiverInRange[callSign].decodeMessage(msg)


    "Emit a ADS-B airborne velocity message"
    def emitAirborneVelocity(self,aircraft):
        msg = ("Velocity", aircraft.icaoAdress, aircraft.heading, aircraft.velocity, aircraft.verticalRate)
        for callSign in self.adsbReceiverInRange:
            self.adsbReceiverInRange[callSign].decodeMessage(msg)

    def emitAircraftStatus(self,aircraft):
        msg = ("AircraftStatus", aircraft.icaoAdress, aircraft.tcasStatus, aircraft.level)
        for callSign in self.adsbReceiverInRange:
            self.adsbReceiverInRange[callSign].decodeMessage(msg)