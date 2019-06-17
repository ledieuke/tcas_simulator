import csv

from aircraft import *

#Time step
DELTA_T = 0.1


class Simulation:
    def __init__(self):
        #List of all aircrafts moving at this current time
        self.aircrafts_moving = []

        #List of all aircrafts that will move in future
        self.aircrafts_waiting = []

        #List of all false aircrafts due to false ADS-B messages
        self.falseAdsbMoving = []

        #Flag to initialize or not the CSV writer
        self.initPlotFlg = True

        #Name of the CSV file to read in data directory
        self.csvfile = None

        #Range between the two targets
        self.range =  None

        #Range rate between the two targets
        self.range_rate = None


    """Initialisation of aircrafts present in the simulation thanks to a csv file"""
    def initialize(self,csvName):
        #Open the csv file
        f = open("simulation/data/" + csvName, "rt")
        reader = csv.reader(f)

        #Pass the header
        next(reader, None)

        #Read each line of the csv file and add a corresponding aircraft to aircrafts_moving or aircrafts_waiting
        for r in reader:
            callSign = r[0]
            icaoAdress = r[1]
            velocity = float(r[2])
            if (r[3] == "NONE"):
                baroaltitude = None
            else:
                baroaltitude = float(r[3])
            if(r[4] == "NONE"):
                geoaltitude = None
            else:
                geoaltitude = float(r[4])
            latitude = float(r[5])
            longitude = float(r[6])
            heading = float(r[7])
            verticalRate = float(r[8])
            if(r[9] == "TRUE"):
                adsbOutStatus = True
            else:
                adsbOutStatus = False
            if(r[10] == "TRUE"):
                tcasStatus = True
            else:
                tcasStatus = False
            if(r[11] == "TRUE"):
                isReal = True
            else:
                isReal = False
            startTime = float(r[12])
            ao = Aircraft(callSign,icaoAdress,velocity,baroaltitude,geoaltitude,latitude,longitude,heading,verticalRate,isReal,adsbOutStatus, tcasStatus,startTime)
            if(ao.startTime < 1e-10):
                self.aircrafts_moving.append(ao)
            else:
                self.aircrafts_waiting.append(ao)


    """Add aircrafts that start to move in aircrafts_moving and remove them from aircrafts_waiting"""
    def waitingToMoving(self, currentTime):
        for a in self.aircrafts_waiting:
            if(a.startTime <= currentTime):
                self.aircrafts_moving.append(a)
                self.aircrafts_waiting.remove(a)
                for am in self.aircrafts_moving:
                    am.adsb.adsbEmitter.emitIdentification(am)
                    am.adsb.adsbEmitter.emitAirbornePosition(am)
                    am.adsb.adsbEmitter.emitAirborneVelocity(am)
                    am.adsb.adsbEmitter.emitAircraftStatus(am)


    """Hacking method that permit to do a DOS of the TCAS"""
    def buildFunnel(self, aircraft):
        for i in range(3, 4):
            falseAdsb1 = Aircraft(aircraft.callSign, "ZOOO0", aircraft.velocity, aircraft.baroaltitude + 100 * (i + 1),
                                  aircraft.geoaltitude + 100 * (i + 1),
                                  aircraft.latitude + (m.cos(m.radians(aircraft.heading - m.pi / 4)) * 250 * i) / (1852 * 60),
                                  aircraft.longitude + (m.sin(m.radians(aircraft.heading - m.pi / 4)) * (250 / m.cos(m.radians(aircraft.latitude))) * i) / (1852 * 60),
                                  aircraft.heading, aircraft.verticalRate, False, False, aircraft.startTime)
            falseAdsb2 = Aircraft(aircraft.callSign, "ZOOO1", aircraft.velocity, aircraft.baroaltitude - 100 * (i + 1),
                                  aircraft.geoaltitude - 100 * (i + 1),
                                  aircraft.latitude - (m.cos(m.radians(aircraft.heading - m.pi / 4)) * 250 * i) / (1852 * 60),
                                  aircraft.longitude + (m.sin(m.radians(aircraft.heading - m.pi / 4)) * (250 / m.cos(m.radians(aircraft.latitude))) * i) / (1852 * 60),
                                  aircraft.heading, aircraft.verticalRate, False, False, aircraft.startTime)
            self.falseAdsbMoving.append(falseAdsb1)
            self.falseAdsbMoving.append(falseAdsb2)


    """Hacking method that put two aircraft at the same altitude"""
    def putOnSameAltitude(self,a1, a2):
        falseAdsb1 = Aircraft(a2.callSign, "ZOOO0", 100, a1.baroaltitude + 100,
                              a1.geoaltitude + 100,
                              a1.latitude + (m.cos(m.radians(a1.heading - m.pi / 4)) * 6000) / (1852 * 60),
                              a1.longitude + (m.sin(m.radians(a1.heading - m.pi / 4)) * (6000 / m.cos(m.radians(a1.latitude)))) / (1852 * 60),
                              (a1.heading + 180) % 360, a1.verticalRate, False, False, a1.startTime)
        falseAdsb2 = Aircraft(a1.callSign, "ZOOO1", 100, a2.baroaltitude - 100,
                              a2.geoaltitude - 100,
                              a2.latitude + (m.cos(m.radians(a2.heading - m.pi / 4)) * 6000) / (1852 * 60),
                              a2.longitude + (m.sin(m.radians(a2.heading - m.pi / 4)) * (6000 / m.cos(m.radians(a2.latitude)))) / (1852 * 60),
                              (a2.heading + 180) % 360, a2.verticalRate, False, False, a1.startTime)
        self.falseAdsbMoving.append(falseAdsb1)
        self.falseAdsbMoving.append(falseAdsb2)

    def hacking(self, currentTime):
        target1 = self.aircrafts_moving[0]
        target2 =self.aircrafts_moving[1]
        if (self.range != None):
            new_range = findHorizontalDistance(target1.latitude, target1.longitude, target2.latitude, target2.longitude)
            self.range_rate = (new_range - self.range)/DELTA_T
            self.range = new_range
        else:
            self.range = findHorizontalDistance(target1.latitude, target1.longitude, target2.latitude, target2.longitude)
            self.range_rate = -1
        for a in self.aircrafts_moving:
            if(len(self.falseAdsbMoving) == 0):
                if(a.adsbOutStatus and a.tcasStatus and ((-self.range/self.range_rate) < 206)):
                    lat, lon = findPositionFromHeadingAndHorizontalDistance(a.latitude, a.longitude, a.heading, 20*1852)[:2]
                    falseAdsb1 = Aircraft("AZE4533", "2563", a.velocity*2, a.baroaltitude+200, a.geoaltitude+200, lat, lon, a.heading, a.verticalRate, False, True, False, a.startTime)
                    #falseAdsb2 = Aircraft("AZE4534", "2564", a.velocity, a.baroaltitude-2000, a.geoaltitude-2000, a.latitude+0.000001, a.longitude, a.heading, a.verticalRate, False, True, True, a.startTime)
                    self.falseAdsbMoving.append(falseAdsb1)
                    #self.falseAdsbMoving.append(falseAdsb2)
            if(len(self.falseAdsbMoving) == 1):
                if(a.onRa):
                    self.falseAdsbMoving[0].verticalRate = a.verticalRate
                    if(self.falseAdsbMoving[0].velocity > a.velocity):
                        self.falseAdsbMoving[0].velocity -= 1
                    for b in self.aircrafts_moving:
                        if (not b.adsbOutStatus and not b.tcasStatus):
                            if (a.baroaltitude < b.baroaltitude + 100 and a.baroaltitude > b.baroaltitude - 100):
                                self.falseAdsbMoving[0].latitude = 0
                else:
                    self.falseAdsbMoving[0].verticalRate = 0
                    #if(self.falseAdsbMoving[0].velocity<1200):
                        #self.falseAdsbMoving[0].velocity = a.velocity*2



    """Actualize the ADS-B and TCAS of other aircrafs in range for each aircraft """
    def inRange(self):
        #Analyze the distance between each aircraft
        for ao1 in (self.aircrafts_moving + self.falseAdsbMoving):
            for ao2 in (self.aircrafts_moving + self.falseAdsbMoving):
                if (ao1 != ao2):
                    lat1 = ao1.latitude
                    lon1 = ao1.longitude
                    if(ao1.geoaltitude == None):
                        alt1 = ao1.baroaltitude
                    else:
                        alt1 = ao1.geoaltitude
                    lat2 = ao2.latitude
                    lon2 = ao2.longitude
                    if(ao2.geoaltitude == None):
                        alt2 = ao2.baroaltitude
                    else:
                        alt2 = ao2.geoaltitude
                    distance = findDistance(lat1,lon1,alt1, lat2, lon2, alt2) / 1852

                    adsbAlreadyPresent = ao2.icaoAdress in ao1.adsb.adsbEmitter.adsbReceiverInRange
                    if( ao1.tcasStatus == True):
                        tcasAlreadyPresent = ao2.icaoAdress in ao1.tcas.tcasEmitter.tcasReceiverInRange

                    #200 nm max ADS-B range and 50 nm max TCAS in range
                    if(distance < 20):
                        if (not adsbAlreadyPresent):
                            ao1.adsb.adsbEmitter.adsbReceiverInRange[ao2.icaoAdress] = ao2.adsb.adsbReceiver
                        if (ao1.tcasStatus == True and not tcasAlreadyPresent and ao2.tcasStatus == True):
                            ao1.tcas.tcasEmitter.tcasReceiverInRange[ao2.icaoAdress] = ao2.tcas.tcasReceiver
                    # else:
                    #     if(ao2.icaoAdress in ao1.aircraftIntruders and ao1.icaoAdress in ao2.aircraftIntruders):
                    #         del ao1.aircraftIntruders[ao2.icaoAdress]
                    #         del ao2.aircraftIntruders[ao1.icaoAdress]
                    #         if(ao1.tcasStatus and ao2.icaoAdress in ao1.tcas.tcasEmitter.tcasReceiverInRange):
                    #             del ao1.tcas.tcasEmitter.tcasReceiverInRange[ao2.icaoAdress]
                    #         if(ao2.tcasStatus and ao1.icaoAdress in ao2.tcas.tcasEmitter.tcasReceiverInRange):
                    #             del ao2.tcas.tcasEmitter.tcasReceiverInRange[ao1.icaoAdress]
                    #         del ao1.adsb.adsbEmitter.adsbReceiverInRange[ao2.icaoAdress]
                    #         del ao2.adsb.adsbEmitter.adsbReceiverInRange[ao1.icaoAdress]
                # else:
                    #     if(adsbAlreadyPresent):
                    #         del ao1.adsb.adsbEmitter.adsbReceiverInRange[ao2.icaoAdress]
                    #         if (ao1.tcasStatus == True and tcasAlreadyPresent and ao2.tcasStatus == True):
                    #             del ao1.tcas.tcasEmitter.tcasReceiverInRange[ao2.icaoAdress]
                    #         del ao1.aircraftIntruders[ao2.icaoAdress]
                    # elif(distance < 200.):
                    #     if (not adsbAlreadyPresent):
                    #         ao1.adsb.adsbEmitter.adsbReceiverInRange[ao2.icaoAdress] = ao2.adsb.adsbReceiver
                    #     if (tcasAlreadyPresent and ao1.tcasStatus == True and ao2.tcasStatus == True):
                    #         del ao1.tcas.tcasEmitter.tcasReceiverInRange[ao2.icaoAdress]
                    # else:
                    #     if (adsbAlreadyPresent):
                    #         del ao1.adsb.adsbEmitter.adsbReceiverInRange[ao2.icaoAdress]
                    #     if (tcasAlreadyPresent and ao1.tcasStatus == True and ao2.tcasStatus == True):
                    #         del ao1.tcas.tcasEmitter.tcasReceiverInRange[ao2.icaoAdress]
                    #     if (ao2.icaoAdress in ao1.aircraftIntruders):
                    #         del ao1.aircraftIntruders[ao2.icaoAdress]


    """Move aircrafts to next position and simulate also the next position of false ADS-B aircrafts"""
    def moving(self):
        for ao in self.aircrafts_moving:
                ao.nextPosition(DELTA_T)
        for ao in self.falseAdsbMoving:
                ao.nextPosition(DELTA_T)


    """Emit ADS-B messages at a particular frequency"""
    def emitAdsb(self, currentTime):
        #ADS-B messages from real aircrafts
        for ao in self.aircrafts_moving:
            if(ao.adsbOutStatus):
                #Each 5 seconds
                if(m.fabs(currentTime%5) < DELTA_T):
                    ao.adsb.adsbEmitter.emitIdentification(ao)
                #Each 1/2 second
                if(m.fabs(currentTime%0.5) < DELTA_T):
                    ao.adsb.adsbEmitter.emitAirbornePosition(ao)
                    ao.adsb.adsbEmitter.emitAirborneVelocity(ao)
                # Each 1 second
                if (m.fabs(currentTime % 1) < DELTA_T):
                    ao.adsb.adsbEmitter.emitAircraftStatus(ao)
            #ADS-B messages from false aircrafts
        for ao in self.falseAdsbMoving:
            #Each 5 seconds
            if(m.fabs(currentTime%5) < DELTA_T):
                ao.adsb.adsbEmitter.emitIdentification(ao)
            # Each 1/2 second
            if(m.fabs(currentTime%0.5) < DELTA_T):
                ao.adsb.adsbEmitter.emitAirbornePosition(ao)
                ao.adsb.adsbEmitter.emitAirborneVelocity(ao)
            # Each 1 second
            if (m.fabs(currentTime % 1) < DELTA_T):
                ao.adsb.adsbEmitter.emitAircraftStatus(ao)


    """Ruun the TCAS system"""
    def tcas(self, currentTime):
        for ao in self.aircrafts_moving:
            if(ao.tcasStatus == True):
                if(ao.initTcas == True):
                    ao.tcas.initTcas()
                    ao.initTcas = False
                ao.tcas.run(currentTime)


    """Initialize the CSV writer in order to plot positions on the CSV"""
    def initPlot(self, csvName):
        self.csvfile = open("simulation/results/" + csvName[:-4] + "_results.csv", 'w', newline='')
        csv_writer = csv.writer(self.csvfile)
        csv_writer.writerow(["TIME", "CALL SIGN", "ICAO ADRESS", "VELOCITY", "ALTITUDE", "LATITUDE", "LONGITUDE", "HEADING", "VERTICAL RATE", "ON RA", "ON CRASH", "IS REAL", "ADSB OUT STATUS"])
        self.initPlotFlg = False


    """Plot positions on the CSV in results directory"""
    def plot(self, currentTime):
        csv_writer = csv.writer(self.csvfile)
        for ao in self.aircrafts_moving:
            time = str(currentTime)
            callSign = ao.callSign
            icaoAdress = ao.icaoAdress
            velocity = str(ao.velocity)
            altitude = str(ao.geoaltitude)
            latitude = str(ao.latitude)
            longitude = str(ao.longitude)
            heading = str(ao.heading)
            verticalRate = str(ao.verticalRate)
            onRa = str(ao.onRa)
            onCrash = str(ao.onCrash)
            isReal = str(ao.isReal)
            adsbOutStatus = str(ao.adsbOutStatus)
            csv_writer.writerow([time,callSign,icaoAdress,velocity,altitude,latitude,longitude,heading,verticalRate,onRa,onCrash,isReal,adsbOutStatus])
            self.csvfile.flush()
        for ao in self.falseAdsbMoving:
            time = str(currentTime)
            callSign = ao.callSign
            icaoAdress = ao.icaoAdress
            velocity = str(ao.velocity)
            altitude = str(ao.geoaltitude)
            latitude = str(ao.latitude)
            longitude = str(ao.longitude)
            heading = str(ao.heading)
            verticalRate = str(ao.verticalRate)
            onRa = str(ao.onRa)
            onCrash = str(ao.onCrash)
            isReal = str(ao.isReal)
            adsbOutStatus = str(ao.adsbOutStatus)
            csv_writer.writerow([time,callSign,icaoAdress,velocity,altitude,latitude,longitude,heading,verticalRate,onRa,onCrash,isReal,adsbOutStatus])
            self.csvfile.flush()


    """Detect if two are in a crash"""
    def crashDetection(self):
        for a1 in self.aircrafts_moving:
            for a2 in self.aircrafts_moving:
                if(a1 != a2):
                    lat1 = a1.latitude
                    lon1 = a1.longitude
                    if (a1.geoaltitude == None):
                        alt1 = a1.baroaltitude
                    else:
                        alt1 = a1.geoaltitude
                    lat2 = a2.latitude
                    lon2 = a2.longitude
                    if (a2.geoaltitude == None):
                        alt2 = a2.baroaltitude
                    else:
                        alt2 = a2.geoaltitude
                    distance = findDistance(lat1, lon1, alt1, lat2, lon2, alt2)

                    #If distance < 40 m => crash
                    if(distance < 40 and a1.isReal and a2.isReal):
                        a1.onCrash = True
                        a2.onCrash = True


    """Start the whole simulation"""
    def start(self, csvName, duration):
        self.initialize(csvName)
        currentTime = 0
        while(currentTime < duration):
            #print("TIME = ", currentTime)
            if (m.fabs(currentTime % 1) < DELTA_T):
                self.waitingToMoving(currentTime)
                self.inRange()
            self.hacking(currentTime)
            self.emitAdsb(currentTime)
            if (m.fabs(currentTime % 0.5) < DELTA_T):
                self.tcas(currentTime)
            if(self.initPlotFlg == True):
                self.initPlot(csvName)
            if (m.fabs(currentTime % 0.5) < DELTA_T):
                self.plot(currentTime)
            self.moving()
            self.crashDetection()
            currentTime += DELTA_T
        self.csvfile.close()


def main_debug():
    simulation = Simulation()

    simulation.start("funnel.csv", 360)

def main(argv):
    simulation = Simulation()

    simulation.start(argv[0], int(argv[1]))


if __name__ == "__main__":
    main(sys.argv[1:])
    # main_debug()
