import csv
import sys
import re

from util import findHorizontalDistance

def main(argv):
    #Open the CSV file to write extracted data
    csvfile = open("simulation/data/extract.csv", 'w', newline='')
    csv_writer = csv.writer(csvfile)

    #Write the header
    csv_writer.writerow(
        ["CALL SIGN", "ICAO ADRESS", "VELOCITY", "BAROALTITUDE", "GEOALTITUDE", "LATITUDE", "LONGITUDE", "HEADING",
         "VERTICAL RATE", "TCAS STATUS", "START TIME"])

    #Open the CSV file to read original data
    f = open("ADSB_data/" + argv[0])
    reader = csv.reader(f)

    #Skip the header
    next(reader, None)

    #Dictionnary gathering all aircrafts
    already_read = {}

    beginningTime = 0

    for r in reader:
        if (beginningTime == 0):
            beginningTime = float(r[15])

        callSign = r[7]
        icaoAdress = r[1]
        velocity = r[4]
        geoaltitude = r[13]
        baroaltitude = r[12]
        latitude = r[2]
        longitude = r[3]
        heading = r[5]
        verticalRate = r[6]
        startTime = str(float(r[15]) - beginningTime)

        if (not (callSign in already_read) and re.search('^ *$', callSign) == None):
            tcasStatus = "TRUE"
            already_read[callSign] = [callSign, icaoAdress, velocity, baroaltitude, geoaltitude, latitude, longitude,
                                        heading, verticalRate, tcasStatus, startTime]

        elif (callSign in already_read):
            if(re.search('^ *$', already_read[callSign][1]) != None):
                already_read[callSign][1] = icaoAdress
            if(re.search('^ *$', already_read[callSign][2]) != None):
                already_read[callSign][2] = velocity
            if(re.search('^ *$', already_read[callSign][3]) != None):
                already_read[callSign][3] = baroaltitude
            if(re.search('^ *$', already_read[callSign][4]) != None):
                already_read[callSign][4] = geoaltitude
            if(re.search('^ *$', already_read[callSign][5]) != None):
                already_read[callSign][5] = latitude
                already_read[callSign][6] = longitude
            if(re.search('^ *$', already_read[callSign][6]) != None):
                already_read[callSign][5] = latitude
                already_read[callSign][6] = longitude
            if(re.search('^ *$', already_read[callSign][7]) != None):
                already_read[callSign][7] = heading
            if(re.search('^ *$', already_read[callSign][8]) != None):
                already_read[callSign][8] = verticalRate


    icaoAdress = 0
    for callSign in already_read:
        flag = True
        for e in already_read[callSign]:
            if(re.search('^ *$', e) != None):
                flag = False
        if(flag):
            callSign = already_read[callSign][0]
            velocity = already_read[callSign][2]
            geoaltitude = already_read[callSign][3]
            baroaltitude = already_read[callSign][4]
            latitude = already_read[callSign][5]
            longitude = already_read[callSign][6]
            heading = already_read[callSign][7]
            verticalRate = already_read[callSign][8]
            tcasStatus = already_read[callSign][9]
            startTime = already_read[callSign][10]
            distance = findHorizontalDistance(float(latitude), float(longitude),  float(argv[1]),  float(argv[2]))
            if (float(geoaltitude) > 2000 and distance < 200*1852):
                csv_writer.writerow([callSign, icaoAdress, velocity, baroaltitude, geoaltitude, latitude, longitude, heading,
                         verticalRate, tcasStatus, startTime])
            icaoAdress += 1


if __name__ == "__main__":
    main(sys.argv[1:])
