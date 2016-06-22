
RATE_OF_UPDATES = 1         # Number of simulated seconds between updates

IS_TEST = False             # Eh... not sure what to call this. Logic testng, print out everything.
OUR_LOCATION = [32.606184, -85.488228]

DELAY = .1                  # Number of seconds between calculations
SIMULATE_TIME = False       # Make it realtime?

NUM_PLANES = 6              # Number of planes to generate
NUM_WAY_POINTS = 10         # Number of waypoints to generate
GRID_SIZE = 500             # Size of grid

MAX_QUEUE_SIZE = 1000       # Maximum queue size
COMM_KILL_TIME = 2          # Number of seconds to wait between updates to kill communication

CRASH_DISTANCE = 12
DISTANCE_FOR_SUCCESS = 2    # Maximum distance to consider a waypoint reached

COLLISION_AVOIDANCE = False # Set collision avoidance to true or false, will use the following parameter
ALGORITHM = 'APF'

DEFAULT_UAV_SPEED = 12      # Default UAV speed in meters per second
MAX_ELEV_ANGLE = 22.5       # Maximum angle of elevation in degrees
MAX_TURN_ANGLE = 22.5       # Maximum turning angle in degrees (Will result in hex shape)
MIN_TURN_RAD = 12           # Minimum turning radius in meters