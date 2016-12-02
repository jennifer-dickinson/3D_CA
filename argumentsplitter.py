import argparse
import sys

from defaultValues import *


def main():
    args = argParser()
    displayArgs(args)


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def argParser():
    parser = MyParser(description="Simulate unmanned aerial vehicle flights", allow_abbrev=False)

    parser.add_argument('-c', '-centralized', type=bool, default=CENTRALIZED, dest='CENTRALIZED', metavar='',
                        help='[ True | False ] choose to run in decentralized mode, %s by default' % CENTRALIZED)

    parser.add_argument('-ca', '-collision-avoidance', type=bool, default=COLLISION_AVOIDANCE,
                        dest='COLLISION_AVOIDANCE',
                        metavar='',
                        help='[ True | False ] enable collision avoidance algorithms, %s by default' % COLLISION_AVOIDANCE)

    parser.add_argument('-a', '-algorithm', default=algorithmChoices[0], dest="ALGORITHM", metavar='',
                        choices=algorithmChoices,
                        help='[ ALGORITHM ] choose anti-collision algorithm, \'%s\' by default' % algorithmChoices[0])

    parser.add_argument('-cd', '-collision-detectance', type=bool,
                        default=COLLISION_DETECTANCE, dest='COLLISION_DETECTANCE', metavar='',
                        help='[ True | False ] UAVs will crash when in close proximity of each other, %s by default' % COLLISION_DETECTANCE)

    parser.add_argument('-s', '-speed', type=float, default=DEFAULT_UAV_SPEED, metavar='', dest="UAV_SPEED",
                        help='[ FLOAT ] set UAV speed in meters per second, %s m/s by default' % DEFAULT_UAV_SPEED)

    parser.add_argument('-p', '-planes', type=int, default=NUM_PLANES, metavar='', dest="NUM_PLANES",
                        help='[ INT ] set number of planes, %s planes by default' % NUM_PLANES)

    parser.add_argument('-w', '-waypoints', type=int, default=NUM_WAY_POINTS, metavar='', dest="NUM_WAYPOINTS",
                        help='[ INT ] set number of waypoints, %s waypoints by default' % NUM_WAY_POINTS)

    parser.add_argument('-l', '-location', type=float, nargs=2, default=OUR_LOCATION, dest='LOCATION',
                        metavar='',
                        help='[ LONGITUDE LATITUDE ] select a location to simulate, default is %s, %s'
                             ' (Auburn University)' % (OUR_LOCATION[0], OUR_LOCATION[1]))

    parser.add_argument('-crd', '-crash-distance', type=float, default=CRASH_DISTANCE, dest="CRASH_DISTANCE",
                        metavar='',
                        help='[ FLOAT ] set crash distance in meters, %s m by default' % CRASH_DISTANCE)

    args = parser.parse_args()

    parser.add_argument('-conflict-distance', type=float, default=args.UAV_SPEED * 2, dest="CONFLICT_DISTANCE",
                        metavar='',
                        help='[ FLOAT ] set conflict distance, default is SPEED * 2')

    parser.add_argument('-del', '-delay', type=float, default=DELAY, dest='DELAY', metavar='',
                        help='[ FLOAT ] number of seconds between calculations, %s s by default' % DELAY)

    parser.add_argument('-g', '-grid', type=int, nargs=2, default=[100, 100], dest='GRID_SIZE', metavar='',
                        help='[ INT INT ] size of grid in meters (length x width)')

    parser.add_argument('-mea', '-max-elevation-angle', type=float, default=MAX_ELEV_ANGLE,
                        dest="MAX_ELEV_ANGLE", metavar='')

    parser.add_argument('-mtr', '-min-turning-radius', type=float, default=MIN_TURN_RAD, dest="MIN_TURN_RAD",
                        metavar='')

    parser.add_argument('-sample', type=bool, default=USE_SAMPLE_SET, dest="USE_SAMPLE_SET", metavar='')

    parser.add_argument('-wpd', '-waypoint-distance', type=int, default=WAYPOINT_DISTANCE, dest='WAYPOINT_DISTANCE',
                        metavar='')

    if parser.parse_args().USE_SAMPLE_SET:
        parser.parse_args().SAMPLE_SET = SAMPLE_WP_SET

    return parser.parse_args()


def displayArgs(args):
    argsList = []
    for arg in vars(args):
        item = getattr(args, arg)
        string = arg + ": " + str(item)
        argsList.append(string)



    for arg in argsList:
        print(arg)


if __name__ == '__main__':
    main()
