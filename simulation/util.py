import  math as m
import numpy as np

"""Return horizontal distance in meters from one point to another point where point is defined by a latitude and a
longitude"""
def findHorizontalDistance(lat1, lon1, lat2, lon2):
    lat = (lat1+lat2)/2
    dlat = m.fabs(lat2-lat1)
    dlon = m.fabs(lon2-lon1)

    x = dlat * 60 * 1852
    y = dlon * 60 * 1852 * m.cos(m.radians(lat))

    horizontalDistance = m.sqrt(m.pow(x,2)+m.pow(y,2))

    return horizontalDistance

def findPositionFromHeadingAndHorizontalDistance(lat, lon, heading, distance):
    distanceLatitudeProjected = distance*m.cos(m.radians(heading))
    dlat = distanceLatitudeProjected / (60*1852)
    lat1, lat2 = lat + dlat, lat - dlat
    distanceLongitudeProjected = m.sqrt(m.pow(distance,2) - m.pow(distanceLatitudeProjected,2))
    dlon = distanceLongitudeProjected / (60 * 1852 * m.cos(m.radians(lat)))
    lon1, lon2 = lon + dlon, lon - dlon
    return lat1, lon1, lat2, lon2

"Return vertical distance in meters between two altitudes"
def findVerticalDistance(alt1, alt2):
    #1 meter = 0.3048 feet
    verticalDistance = m.fabs(alt1 - alt2) * 0.3048
    return verticalDistance


"""Return horizontal distance in meters from one point to another point where point is defined by a latitude,
a longitude and an altitude"""
def findDistance(lat1, lon1, alt1, lat2, lon2, alt2):
    horizontalDistance = findHorizontalDistance(lat1, lon1, lat2, lon2)
    verticalDistance = findVerticalDistance(alt1, alt2)

    distance = m.sqrt(m.pow(horizontalDistance,2) + m.pow(verticalDistance,2))

    return distance


def findHeading(lat1, lon1, lat2, lon2):
    lat_distance = findHorizontalDistance(lat1, 0, lat2, 0)
    distance = findHorizontalDistance(lat1, lon1, lat2, lon2)

    heading = m.acos(lat_distance/distance)

    return heading

# Return a perpendicular vector with the same norm
def perpendicularVector(v):
    return np.array([v[1], -v[0]])


# Return the relative position S in nautic miles from one point to another point where point is defined by a latitude and a longitude
def findRelativeHorizontalPosition(aircraft, aircraftIntruder):
    lat1 = aircraft.latitude
    lat2 = aircraftIntruder.latitude
    lon1 = aircraft.longitude
    lon2 = aircraftIntruder.longitude

    heading = findHeading(lat1, lon1, lat2, lon2)
    distance = findHorizontalDistance(lat1, lon1, lat2, lon2)

    if(lat1 > lat2):
        s_x = distance * m.cos(heading)
    else:
        s_x = -distance * m.cos(heading)

    if(lon1 < lon2):
        s_y = -distance * m.sin(heading)
    else:
        s_y = distance * m.sin(heading)

    s = np.array([s_x,s_y]) / 1852

    return s


#Feet
def findRelativeVerticalPosition(aircraft, aircraftIntruder):
    s1_z = aircraft.altitude
    s2_z = aircraftIntruder.altitude

    s_z = s1_z - s2_z

    return s_z


#Nautical miles per seconds
def findRelativeHorizontalVelocity(aircraft, aircraftIntruder):
    v1 = aircraft.velocity
    heading1 = aircraft.heading
    v2 = aircraftIntruder.velocity
    heading2 = aircraftIntruder.heading

    v1_x = v1 * m.cos(m.radians(heading1))
    v1_y = v1 * m.sin(m.radians(heading1))

    v2_x = v2 * m.cos(m.radians(heading2))
    v2_y = v2 * m.sin(m.radians(heading2))

    v_x = v1_x - v2_x
    v_y = v1_y - v2_y

    v = np.array([v_x,v_y]) / 3600

    return v


#Feet per seconds
def findRelativeVerticalVelocity(aircraft, aircraftIntruder):
    v1_z = aircraft.verticalRate
    v2_z = aircraftIntruder.verticalRate

    v_z = (v1_z - v2_z) / 60

    return v_z
