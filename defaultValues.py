CENTRALIZED = False  # True or false
COLLISION_AVOIDANCE = False  # Set collision avoidance to true or false, will use the following parameter
ALGORITHM = 'APF'

DEFAULT_UAV_SPEED = 12  # Default UAV speed in meters per second
MAX_ELEV_ANGLE = 22.5  # Maximum angle of elevation in degrees
MAX_TURN_ANGLE = 22.5  # Maximum turning angle in degrees (Will result in hex shape)
MIN_TURN_RAD = 28.64058013  # Minimum turning radius in meters

OUR_LOCATION = [32.606184, -85.488228]

DELAY = .2  # Number of seconds between calculations

<<<<<<< HEAD
NUM_PLANES = 20  # Number of planes to generate
=======
NUM_PLANES = 4  # Number of planes to generate
>>>>>>> origin/master
NUM_WAY_POINTS = 10  # Number of waypoints to generate
GRID_SIZE = 20  # Size of grid

COMM_KILL_TIME = 2  # Number of seconds to wait between updates to kill communication

CRASH_DISTANCE = 2  # Distance to be considered a crash (meters)
CONFLICT_DISTANCE = DEFAULT_UAV_SPEED * 2
WAYPOINT_DISTANCE = 2  # Maximum distance to consider a waypoint reached (meters)

<<<<<<< HEAD
COLLISION_AVOIDANCE = False  # Set collision avoidance to true or false, will use the following parameter
ALGORITHM = 'APF'

DEFAULT_UAV_SPEED = 12  # Default UAV speed in meters per second
MAX_ELEV_ANGLE = 22.5  # Maximum angle of elevation in degrees
MAX_TURN_ANGLE = 22.5  # Maximum turning angle in degrees (Will result in hex shape)
MIN_TURN_RAD = 28.64058013  # Minimum turning radius in meters

CENTRALIZED = False  # True or false
=======
LATITUDE_TO_METERS = 110574.61  # Meters per latitude degree
LONGITUDE_TO_METERS = 111302.62  # Meters per longitiude degree
>>>>>>> origin/master
