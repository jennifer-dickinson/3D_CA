# Originally this was going to be an initializer... So far I've just been throwing stuff in here
# Actual things on ran on test.py

import standardFuncs


is_test = False

# Generate a latitude, longitude grid according to the size of the airspace.
# Maximum range for xbee telemetry module is 2 miles (Approx. 3218 meters)
def generateGrid(grid_size, location):
    lat_ll = location[0] - (grid_size / (2 * standardFuncs.LATITUDE_TO_METERS))  # Set lower latitude limit
    lat_ul = location[0] + (grid_size / (2 * standardFuncs.LATITUDE_TO_METERS))  # Set upper latitude limit
    lon_ll = location[1] - (grid_size / (2 * standardFuncs.LONGITUDE_TO_METERS))  # Set lower longitude limit
    lon_ul = location[1] + (grid_size / (2 * standardFuncs.LONGITUDE_TO_METERS))  # Set upper longitude limit

    # Return as a list
    grid = [[lat_ll, lat_ul], [lon_ll, lon_ul]]
    return grid
