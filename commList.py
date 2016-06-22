import threading
import time
import defaultValues

from collections import deque, namedtuple

info = namedtuple('info', 'id latitude longitude altitude')

class uavComm(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.positions = list()
        self.go = True
        self.timer = 0
        self.timer_updates = 0

    def run(self):
        while self.go:
            time.sleep(defaultValues.DELAY)
            #print "Communication is up and running."

            # Increment timer with each loop. If no updates after threshold, break.
            self.timer += defaultValues.DELAY
            if self.timer > defaultValues.COMM_KILL_TIME:
                print "Communication timed out"
                break

        print "Communication has ended.\n"
        print "Last positions for UAVs:"
        for elem in self.positions:
            status = 'survived'
            if elem['dead'] == True:
                status = "crashed"
            print "UAV ID:", elem["ID"], "at position", elem["cLoc"], status

        for elem in self.positions:
            print elem

    def startUp (self, plane):
        dict = {"ID" : plane.id, "cLoc" : plane.cLoc, "bear": plane.cBearing, "elev": plane.cElevation, "dead" : plane.dead, "killedBy" : None }
        self.positions.append(dict)
        self.timer = 0
        print "Initial position for UAV", plane.id, "updated!"

    def update(self, plane):
        dict = (item for item in self.positions if item["ID"] == plane.id).next()
        dict["cLoc"] = plane.cLoc
        dict["bear"] = plane.cBearing
        dict["elev"] = plane.cElevation
        dict["tdis"] = plane.tdistance
        if plane.dead:
            dict["dead"] = plane.dead
            dict["killedBy"] = plane.killedBy
            dict2 = (item for item in self.positions if item["ID"] == plane.killedBy).next()
            dict2["dead"] = plane.dead
            dict2["killedBy"] = plane.id
        self.timer = 0
        return True

    def read(self):
        return self.positions
        pass

    # Ends the thread
    def stop(self):
        self.go = False
