from threading import Thread, Event, RLock
import time
import defaultValues

from collections import deque, namedtuple

info = namedtuple('info', 'id latitude longitude altitude')
DEGREE= u'\N{DEGREE SIGN}'

class uavComm(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.positions = list()
        self.stopped = False

        self.timer = 0
        self.counter = 0
        self.total_uavs = 0     # Total number of UAVs in the air
        self.steps_counter = 0

        self.writeState = Event()
        self.readState = Event()

        self.lock = RLock()
        self.lock2 = RLock()
        try:
            self.readState.set()
        except:
            print "Read state not set"
        if self.readState.isSet(): print "Read state set!"

    def run(self):
        while not self.stopped or self.total_uavs != 0:

            time.sleep(1)
            #print "Communication is up and running."

            # Increment timer with each loop. If no updates after threshold, break.
            self.timer += 1

            if self.timer > 5:
                print "Communication timed out"
                print "UAV counter set to %.f" % self.counter
                print "Read state set to %s" % self.readState.isSet()
                self.stopped = True
                break
            if self.timer > 4:
                try: self.lock.release()
                except: pass


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
        print "%.f total steps taken." % self.steps_counter

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
        self.writeState.wait()
        self.lock.acquire()
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
            # Just in case the other plane still thinks its alive.
            dict2 = (item for item in self.positions if item["ID"] == plane.killedBy).next()
            if  dict2["dead"] == False:
                dict2["dead"] = plane.dead
                dict2["killedBy"] = plane.id
                self.total_uavs -= 1

        self.timer = 0  # Reset timer
        self.counter += 1
        if self.counter >= self.total_uavs:
            self.counter = 0
            self.steps_counter += 1
            self.writeState.clear()
            self.readState.set()
            #print "States switched!"
        #print "Position updated for UAV #%i." % plane.id
        self.lock.release()
        #print "Lock released!"

    def read(self):
        #print "Running read"
        self.readState.wait()
        #print "Read accessed"
        self.lock2.acquire()
        list = []
        while not list:
            list = self.positions

        self.counter += 1
        if self.counter >= self.total_uavs:
            self.counter = 0
            try:
                self.readState.clear()
                self.writeState.set()
                #print "Switch to write state"
            except:
                #print "Could not switch states"
                pass
        self.lock2.release()
        #print "LOCK 2 RELEASED"
        return list


    # Ends the thread
    def stop(self):
        self.stopped = True
