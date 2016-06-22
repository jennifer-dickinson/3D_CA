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
            print "Communication is up and running."

        print "Communication has ended."
        print "Last positions for UAVs:"
        for elem in self.positions:
            print "UAV ID:", elem["ID"], "at position", elem["cLoc"]

    def startUp (self, plane):
        dict = {"ID" : plane.id, "cLoc" : plane.cLoc, "pLoc": plane.pLoc, "dead" : False}
        self.positions.append(dict)
        self.timer = 0
        print "Initial position for UAV", plane.id, "updated!"

    def update(self, plane):
        dict = (item for item in self.positions if item["ID"] == plane.id).next()
        dict["cLoc"] = plane.cLoc
        dict["pLoc"] = plane.pLoc
        self.timer = 0

    def read(self):
        return self.positions
        pass

    # Ends the thread
    def stop(self):
        self.go = False
