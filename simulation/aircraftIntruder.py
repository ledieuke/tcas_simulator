class AircraftIntruder:

    def __init__(self):
        self.callSign = None
        self.icaoAdress = None

        #Velocity in knots
        self.velocity = None

        #Altitude in feet
        self.altitude = None

        #Latitude in degrees
        self.latitude = None

        #Longitude in degrees
        self.longitude = None

        #Heading in degrees
        self.heading = None

        #Vertical rate in feet per minutes
        self.verticalRate = None

        #Sensitivity level
        self.level = None

        #Intruder is TCAS equiped
        self.tcas = None




    """Re-write the print method"""
    def __str__(self):
        return ("Call Sign = " + self.callSign + ", ICAO Adress = " + self.icaoAdress + ", Latitude = " +
                str(self.latitude) + ", Longitude = " + str(self.longitude) + ", Altitude = " + str(self.altitude) +
                " feet, Heading = " + str(self.heading) + ", Velocity = " + str(self.velocity) +
                " knots, Vertical Rate = " + str(self.verticalRate) + " feet/min")