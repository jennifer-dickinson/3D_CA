# Converted from CPP to from David Jone's original UAV program
# Modified to use Haversine's formula for angle of bearing and horizontal distance
# Included three dimensional distance formula and angle of elevation
# Dropped new waypoint calculator
# Added constants

import math
import collections
import logging
import time
import os

### Note: these are only accurate near the equator
## Todo: make a function that vary thise variables depending on location
LATITUDE_TO_METERS = 110574.61  # Meters per latitude degree
LONGITUDE_TO_METERS = 111302.62  # Meters per longitiude degree

DEGREE = u'\N{DEGREE SIGN}'


# Convert cardinal direction to an angle in the cartesian plane
def to_cartesian(uav_bearing):
    uav_bearing = manipulate_angle(uav_bearing)

    if 180.0 > uav_bearing >= 0:  # 1st or 4th quadrant
        return 90.0 - uav_bearing
    elif 0 > uav_bearing >= -90.0:  # 2nd quadrant
        return -1 * uav_bearing + 90
    elif -90.0 > uav_bearing > -180.0:  # third quadrant
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
def findDistance(coor1, coor2):
    lat1 = coor1.latitude
    lat2 = coor2.latitude
    lon1 = coor1.longitude
    lon2 = coor2.longitude
    R = 6378.137  # Radius of the earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c * 1000
    return distance  # total distance in meters


# Calculate total distance
def totalDistance(coor1, coor2):
    d_hor = findDistance(coor1, coor2)
    d_alt = coor2.altitude - coor1.altitude
    distance = math.sqrt(math.pow(d_hor, 2) + math.pow(d_alt, 2))
    return distance


# Return bearing using Haversine's formula, in degrees
def find_bearing(coor1, coor2):
    lat1 = coor1.latitude
    lat2 = coor2.latitude
    lon1 = coor1.longitude
    lon2 = coor2.longitude
    angle = math.atan2(math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1),
                       math.sin(lon2 - lon1) * math.cos(lat2))
    angle = to_cartesian(math.degrees(angle))
    return angle


# Return angle of elevation in spherical coordinates
def elevation_angle(coor1, coor2):
    h_dis = findDistance(coor1, coor2)
    a_dis = coor2.altitude - coor1.altitude
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


# Generate a latitude, longitude grid according to the size of the airspace.
# Maximum range for xbee telemetry module is 2 miles (Approx. 3218 meters)
def generateGrid(grid_size, location):
    lat_ll = location[0] - (grid_size / (2 * LATITUDE_TO_METERS))  # Set lower latitude limit
    lat_ul = location[0] + (grid_size / (2 * LATITUDE_TO_METERS))  # Set upper latitude limit
    lon_ll = location[1] - (grid_size / (2 * LONGITUDE_TO_METERS))  # Set lower longitude limit
    lon_ul = location[1] + (grid_size / (2 * LONGITUDE_TO_METERS))  # Set upper longitude limit

    # Return as a list
    grid = [[lat_ll, lat_ul], [lon_ll, lon_ul]]
    return grid


def logger():
    # datetime = time.time()
    # if not os.path.exists("%s" % datetime):
    #     os.makedirs("%s" % datetime)
    # logging.basicConfig(filename='logs/%s/debug.log' % datetime, filemode='w',
    #                     format='%(asctime)s [%(levelname)s]: %(message)s',
    #                     level=logging.DEBUG)
    logging.basicConfig(filename='logs/debug.log', filemode='w', format='%(asctime)s [%(levelname)s]: %(message)s',
                        level=logging.DEBUG)
