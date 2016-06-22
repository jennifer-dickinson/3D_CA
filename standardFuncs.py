# Converted from CPP to from David Jone's original UAV program
# Modified to use Haversine's formula for angle of bearing and horizontal distance
# Included three dimensional distance formula and angle of elevation
# Dropped new waypoint calculator
# Added constants

import math
import collections

### Note: these are only accurate near the equator
## Todo: make a function that vary thise variables depending on location
LATITUDE_TO_METERS = 110574.61   # Meters per latitude degree
LONGITUDE_TO_METERS = 111302.62  # Meters per longitiude degree


# Convert cardinal direction to an angle in the cartesian plane
def to_cartesian(uav_bearing):
    uav_bearing = manipulate_angle(uav_bearing)

    if 180.0 > uav_bearing >= 0: #1st or 4th quadrant
        return 90.0 - uav_bearing
    elif 0 > uav_bearing >= -90.0: #2nd quadrant
        return -1 * uav_bearing + 90
    elif -90.0 > uav_bearing > -180.0: #third quadrant
        return -1 * (uav_bearing + 180.0) - 90.0
    elif uav_bearing == 180.0 or uav_bearing == -180.0:
        return -90.0
    else:
        return -999  # should never happen


# Convert angle in the cartesian pane to a cardinal direction
def to_cardinal(angle):
    angle = manipulate_angle(angle)

    if 90.0 >= angle >= -90.0:
        return 90 - angle
    elif 90.0 <= angle <= 180.0:
        return -1 * angle + 90.0
    elif -90.0 >= angle >= -180.0:
        return -180.0 + -1 * (90 + angle)
    else:
        return -999  # should never happen


# Modify the angle so that it remains on the interval [-180,180]

def manipulate_angle(angle):
    while angle > 180.0:
        angle -= 360
    while angle < -180.0:
        angle += 360
    return angle


# Calculate relative horizontal distance using Haversine's formula
def horizontal_distance(lat1, lon1, lat2, lon2):
    # type: (starting altitude, starting longitude, final altitude, final longitude) -> distance
    R = 6378.137  # Radius of the earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c * 1000
    return distance  # total distance in meters


# Calculate total distance
def total_distance(lat1, lon1, alt1, lat2, lon2, alt2):
    d_hor = horizontal_distance(lat1, lon1, lat2, lon2)
    d_alt = alt2 - alt1
    distance = math.sqrt(math.pow(d_hor, 2) + math.pow(d_alt, 2))
    return distance


# Calculate total distance
def nt_total_distance(coor1, coor2):
    d_hor = horizontal_distance(coor1.latitude, coor1.longitude, coor2.latitude, coor2.longitude)
    d_alt = coor2.altitude - coor1.altitude
    distance = math.sqrt(math.pow(d_hor, 2) + math.pow(d_alt, 2))
    return distance



# Return bearing using Haversine's formula, in degrees
def find_bearing(lat1, lon1, lat2, lon2):
    angle = math.atan2(math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1),
                       math.sin(lon2 - lon1) * math.cos(lat2))
    angle = to_cartesian(math.degrees(angle))
    return angle


# Return angle of elevation in spherical coordinates
def elevation_angle(lat1, lon1, alt1, lat2, lon2, alt2):
    h_dis = horizontal_distance(lat1, lon1, lat2, lon2)
    a_dis = alt2 - alt1
    angle = math.degrees(math.atan2(a_dis, h_dis))
    return angle


# Returns the sign of the double
def find_sign(number):
    if number > 0:
        return 1
    if number < 0:
        return 0
    return 0

loc = collections.namedtuple('coordinate', 'latitude longitude altitude')