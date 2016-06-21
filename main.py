# Originally this was going to be an initializer... So far I've just been throwing stuff in here
# Actual things on ran on test.py

from standardFuncs import *


is_test = False
frequency = 6  # times per second. Frequency of movementSimulator to calculate stufffffff
rate_of_updates = 5  # seconds per update. Frequency of updates
ourLatLon = [32.606184, -85.488228, 0]  # Approximate cardinal location of the Shelby Center in degrees.


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
