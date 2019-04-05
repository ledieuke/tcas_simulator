from aircraftIntruder import AircraftIntruder


class AdsbReceiver:
    def __init__(self, aircraftIntruders):
        #Same dictionary that the aircraft owning has
        self.aircraftIntruders = aircraftIntruders


    def decodeMessage(self,adsbMessage):
        #type of the ADS-B message
        type = adsbMessage[0]

        #Switch case ADS-B messages
        if(type == "Identification"):
            icaoAdress = adsbMessage[1]

            if(icaoAdress not in self.aircraftIntruders):
                callSign = adsbMessage[2]

                #Aircraft owning gets ICAO Adress and call sign
                self.aircraftIntruders[icaoAdress] = AircraftIntruder()
                self.aircraftIntruders[icaoAdress].icaoAdress = icaoAdress
                self.aircraftIntruders[icaoAdress].callSign = callSign


        elif(type == "SurfacePosition"):
            icaoAdress = adsbMessage[1]

            if (icaoAdress in self.aircraftIntruders):
                heading = adsbMessage[2]
                latitude = adsbMessage[3]
                longitude = adsbMessage[4]

                #Aircraft owning gets ICAO Adress, heading, latitude and longitude
                self.aircraftIntruders[icaoAdress].heading = heading
                self.aircraftIntruders[icaoAdress].latitude = latitude
                self.aircraftIntruders[icaoAdress].longitude = longitude


        elif(type == "AirbornePosition"):
            icaoAdress = adsbMessage[1]

            if (icaoAdress in self.aircraftIntruders):
                baroaltitude = adsbMessage[2]
                geoaltitude = adsbMessage[3]
                latitude = adsbMessage[4]
                longitude = adsbMessage[5]
                level = adsbMessage[6]


                #Aircraft gets ICAO Adress, altitude, latitude and longitude
                self.aircraftIntruders[icaoAdress].baroaltitude = baroaltitude
                self.aircraftIntruders[icaoAdress].geoaltitude = geoaltitude
                self.aircraftIntruders[icaoAdress].latitude = latitude
                self.aircraftIntruders[icaoAdress].longitude = longitude
                self.aircraftIntruders[icaoAdress].level = level


        elif(type == "Velocity"):
            icaoAdress = adsbMessage[1]

            if (icaoAdress in self.aircraftIntruders):
                heading = adsbMessage[2]
                velocity = adsbMessage[3]
                verticalRate = adsbMessage[4]

                #Aircraft gets ICAO Adress, heading, velocity and vertical rate
                self.aircraftIntruders[icaoAdress].heading = heading
                self.aircraftIntruders[icaoAdress].velocity = velocity
                self.aircraftIntruders[icaoAdress].verticalRate = verticalRate


        elif(type == "AircraftStatus"):
            icaoAdress = adsbMessage[1]

            if (icaoAdress in self.aircraftIntruders):
                tcasStatus = adsbMessage[2]
                level = adsbMessage[3]

                #Aircraft gets ICAO Adress and TCAS Status
                self.aircraftIntruders[icaoAdress].tcasStatus = tcasStatus
                self.aircraftIntruders[icaoAdress].level = level