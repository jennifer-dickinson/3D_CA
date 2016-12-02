import argparse
import sys
import textwrap

from defaultValues import *


def main():
    argParser()


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

    def displayArgs(self):

        args = self.parse_args()

        argsList = []
        for arg in vars(args):
            if arg != 'SAMPLE_WP_SET':
                item = getattr(args, arg)
                string = arg.replace('_', ' '), str(item)
                argsList.append(string)

        argsList.sort()

        print("SETTINGS")
        for arg in argsList:
            print(arg[0].lower().capitalize() + ": " + arg[1])

    def setSamlple(self):
        self.SAMPLE_WP_SET = SAMPLE_WP_SET


def algorithms():
    string = ""
    for substring in algorithmChoices[:-1]:
        string += ('\'' + substring + '\', ')
    string += 'or \'' + (algorithmChoices[-1]) + '\''

    return string


description = '''
3D_CA was developed as part of the undergraduate research experience  at Auburn
University during the  Summer 2016  SMART UAV research program.  The purpose of
this program is to provide an easy way to simulatecentralized and decentralized
collision avoidance in autonomous unmanned aerial vehicles (UAV) and to provide
an easy to work with modular platform to implement and test collision avoidance
algorithms.'''


def argParser():
    parser = MyParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False)

    parser.add_argument('-dc', '-centralized', type=bool, default=True, dest='CENTRALIZED', metavar='',
                        help='choose to run in centralized mode, %s by default' % CENTRALIZED)

    parser.add_argument('-ca', '-collision-avoidance', type=bool, default=COLLISION_AVOIDANCE,
                        dest='COLLISION_AVOIDANCE',
                        metavar='',
                        help='[ True | False ] enable collision avoidance algorithms, %s by default' % COLLISION_AVOIDANCE)

    parser.add_argument('-a', '-algorithm', default=algorithmChoices[0], dest="ALGORITHM", metavar='',
                        choices=algorithmChoices,
                        help='[ ALGORITHM ] choose anti-collision algorithm of %s, \'%s\' by default' % (
                            algorithms(), algorithmChoices[0]))

    parser.add_argument('-cd', '-collision-detectance', type=bool,
                        default=COLLISION_DETECTANCE, dest='COLLISION_DETECTANCE', metavar='',
                        help='[ True | False ] UAVs will crash when in close proximity of each other, %s by default' % COLLISION_DETECTANCE)

    parser.add_argument('-s', '-speed', type=float, default=DEFAULT_UAV_SPEED, metavar='', dest="UAV_SPEED",
                        help='[ FLOAT ] set UAV speed in meters per second, %.2fm/s by default' % DEFAULT_UAV_SPEED)

    parser.add_argument('-p', '-planes', type=int, default=NUM_PLANES, metavar='', dest="NUM_PLANES",
                        help='[ INT ] set number of planes, %i planes by default' % NUM_PLANES)

    parser.add_argument('-w', '-waypoints', type=int, default=NUM_WAY_POINTS, metavar='', dest="NUM_WAYPOINTS",
                        help='[ INT ] set number of waypoints, %i waypoints by default' % NUM_WAY_POINTS)

    parser.add_argument('-l', '-location', type=float, nargs=2, default=OUR_LOCATION, dest='LOCATION',
                        metavar='',
                        help='[ LONGITUDE LATITUDE ] select a location to simulate, default is %.3f\N{DEGREE SIGN}, %.3f\N{DEGREE SIGN}'
                             ' (Auburn University)' % (OUR_LOCATION[0], OUR_LOCATION[1]))

    parser.add_argument('-crd', '-crash-distance', type=float, default=CRASH_DISTANCE, dest="CRASH_DISTANCE",
                        metavar='',
                        help='[ FLOAT ] set crash distance in meters, %.2fm by default' % CRASH_DISTANCE)

    parser.add_argument('-cfd', '-conflict-distance', type=float, default=CONFLICT_DISTANCE,
                        dest="CONFLICT_DISTANCE",
                        metavar='',
                        help='[ FLOAT ] set conflict distance, default is SPEED * 2')

    parser.add_argument('-del', '-delay', type=float, default=DELAY, dest='DELAY', metavar='',
                        help='[ FLOAT ] number of seconds between calculations, %.2fs by default' % DELAY)

    parser.add_argument('-g', '-grid', type=int, nargs=2, default=GRID_SIZE, dest='GRID_SIZE', metavar='',
                        help='[ INT INT ] size of grid in meters, %imx%im by default' % (GRID_SIZE[0], GRID_SIZE[1]))

    parser.add_argument('-maxa', '-max-elevation-angle', type=float, default=MAX_ELEV_ANGLE,
                        dest="MAX_ELEV_ANGLE", metavar='',
                        help='[ FLOAT ] set the maximum angle of elevation in degrees, %s\N{DEGREE SIGN} by default' % MAX_ELEV_ANGLE)

    parser.add_argument('-minr', '-min-turn-radius', type=float, default=MIN_TURN_RAD, dest="MIN_TURN_RAD",
                        metavar='',
                        help="[ FLOAT ] set the maximum turning radius in meters, %.2fm by default" % MIN_TURN_RAD)

    parser.add_argument('-wpd', '-waypoint-distance', type=int, default=WAYPOINT_DISTANCE, dest='WAYPOINT_DISTANCE',
                        metavar='',
                        help='[ INT ] set the number of waypoints assigned to each plane, %i by default' % WAYPOINT_DISTANCE)

    parser.add_argument('-samplewp', action='store_true', dest="USE_SAMPLE_SET",
                        help='use a sample set of 10 planes and 64 waypoints per plane, otherwise random waypoints are generated for assigned number of planes')

    parser.add_argument('-settings', action='store_true', dest="DISPLAY",
                        help='display current settings')

    if parser.parse_args().USE_SAMPLE_SET:
        parser.add_argument('-SAMPLE_WP_SET', default=SAMPLE_WP_SET, help=argparse.SUPPRESS)
    if parser.parse_args().DISPLAY:
        parser.displayArgs()

    return parser.parse_args()


if __name__ == '__main__':
    main()
