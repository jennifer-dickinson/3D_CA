import threading
import time
import defaultValues

from collections import deque, namedtuple

info = namedtuple('info', 'id latitude longitude altitude')
DEGREE= u'\N{DEGREE SIGN}'

class uavComm(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.positions = list()
        self.go = True

        self.timer = 0
        self.counter = 0
        self.total_uavs = 0     # Total number of UAVs in the air

        self.writeState = False

    def run(self):
        while self.go:
            time.sleep(defaultValues.DELAY)
            #print "Communication is up and running."

            # Increment timer with each loop. If no updates after threshold, break.
            self.timer += defaultValues.DELAY
            self.counter += 1

            if self.timer > defaultValues.COMM_KILL_TIME:
                print "Communication timed out"
                break

        print "\nCommunication has ended.\n"
        print "LAST POSITION FOR UAVS\n"

        for elem in self.positions:
            print "\nUAV #%.0f's final position at (%.7f%s, %.7f%s, %.2fm) %s." % (
                elem["ID"],
                elem["cLoc"].latitude, DEGREE,
                elem["cLoc"].longitude, DEGREE,
                elem["cLoc"].altitude,
                ("collided with UAV #%.0f" % elem["killedBy"] if elem["dead"] else "survived")
            )
            print "Traveled %.2f meters." % elem["tdis"]
            print "Achieved %.0f waypoint(s)." % elem["wpts"]

        print "\nTotal UAVS still alive: %.0f." % self.total_uavs

    def startUp (self, plane):
        dict = {"ID" : plane.id,
                "cLoc" : plane.cLoc,
                "bear": plane.cBearing,
                "elev": plane.cElevation,
                "dead" : plane.dead,
                "killedBy" : None,
                "wpts" : 0,
                "tdis" : 0
                }
        self.positions.append(dict)
        self.timer = 0
        self.total_uavs += 1
        print "Initial position for UAV", plane.id, "updated!"

    def update(self, plane):
        dict = (item for item in self.positions if item["ID"] == plane.id).next()
        dict["cLoc"] = plane.cLoc
        dict["bear"] = plane.cBearing
        dict["elev"] = plane.cElevation
        dict["tdis"] = plane.distanceTraveled
        if dict["wpts"] < plane.wpAchieved:
            dict["wpts"] = plane.wpAchieved
            print "UAV #%.0f achieved waypoint #%.0f." % (dict["ID"], dict["wpts"])
        if plane.dead and dict["dead"] == False:
            dict["dead"] = plane.dead
            dict["killedBy"] = plane.killedBy
            self.total_uavs -= 1

            # Wont need this if synchronization is enabled
            dict2 = (item for item in self.positions if item["ID"] == plane.killedBy).next()
            if  dict2["dead"] == False:
                dict2["dead"] = plane.dead
                dict2["killedBy"] = plane.id
                self.total_uavs -= 1

        self.timer = 0
        return True

    def read(self):
        return self.positions
        pass

    # Ends the thread
    def stop(self):
        self.go = False
