import math as m

from adsb import *
from tcas import *

class Aircraft:

    def __init__(self,callSign,icaoAdress,velocity,baroaltitude,geoaltitude,latitude,longitude,heading,verticalRate,isReal, adsbOutStatus, tcasStatus,startTime):
        self.callSign = callSign
        self.icaoAdress = icaoAdress

        #Velocity in knots
        self.velocity = velocity

        #Altitude in feet
        self.baroaltitude = baroaltitude

        self.geoaltitude = geoaltitude

        #Latitude in degrees
        self.latitude = latitude

        #Longitude in degrees
        self.longitude = longitude

        #Heading in degrees
        self.heading = heading

        #Vertical rate in feet per minutes
        self.verticalRate = verticalRate

        #Horizontal elevator incidence
        self.alpha = 0

        self.isReal = isReal

        self.adsbOutStatus = adsbOutStatus

        #TCAS equiped
        self.tcasStatus = tcasStatus

        #Init TCAS flag
        if(tcasStatus == True):
            self.initTcas = True
            self.tcas = Tcas(self)
        else:
            self.initTcas = False

        self.onRa = False

        #Sensitivity level
        self.level = 3

        #Dictionary of each aircraft visible for the aircraft , key = ICAO Adress and
        #content = Aircraft Intruder Object
        self.aircraftIntruders = {}

        #Attach an ADS-B system
        self.adsb = Adsb(self.aircraftIntruders)

        self.startTime = startTime

        self.onCrash = False

        self.hackingOn = False

        self.dos = False


    """Re-write the print method"""
    def __str__(self):
        return ("Call Sign = " + self.callSign + ", ICAO Adress = " + self.icaoAdress + ", Latitude = " +
                str(self.latitude) + ", Longitude = " + str(self.longitude) + ", Altitude = " + str(self.altitude) +
                " feet, Heading = " + str(self.heading) + ", Velocity = " + str(self.velocity) +
                " knots, Vertical Rate = " + str(self.verticalRate) + " feet/min" + "TCAS equiped = " + str(self.tcas))


    """Modificate the current position to the next one after delta t seconds"""
    def nextPosition(self, deltaT):
        self.baroaltitude = self.baroaltitude + (self.verticalRate*deltaT)/60
        self.geoaltitude = self.geoaltitude + (self.verticalRate*deltaT)/60

        v_x = (self.velocity*m.cos(m.radians(self.heading)))/3600
        v_y = (self.velocity*m.sin(m.radians(self.heading)))/3600

        self.latitude = self.latitude + (v_x*deltaT)/60
        self.longitude = self.longitude + (v_y*deltaT)/(60*m.cos(m.radians(self.latitude)))

        #North and South poles changes
        if (self.latitude > 90):
            self.latitude = self.latitude - (self.latitude - 90)
            if(self.longitude > 0):
                self.longitude = self.longitude - 180
            else:
                self.longitude = self.longitude + 180
            self.heading = (self.heading + 180) % 360
        elif (self.latitude < -90.):
            self.latitude = self.latitude - (self.latitude + 90)
            if(self.longitude > 0):
                self.longitude = self.longitude - 180
            else:
                self.longitude = self.longitude + 180
            self.heading = (self.heading + 180) % 360

        #Greenwich antimeridian changes
        if (self.longitude > 180.):
            self.longitude -= 360.
        elif (self.longitude < -180.):
            self.longitude += 360.
